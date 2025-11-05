using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Windows.Input;
using KDS.Dashboard.WPF.Helpers;
using KDS.Dashboard.WPF.Models;
using KDS.Dashboard.WPF.Services;

namespace KDS.Dashboard.WPF.ViewModels
{
    /// <summary>
    /// ViewModel for the Features tab showing KDS feature inventory.
    /// Scans prompts/, scripts/, kds-brain/, tests/ to discover features.
    /// Validates code existence, tests, docs, and agent integration.
    /// </summary>
    public class FeaturesViewModel : ViewModelBase
    {
        private ObservableCollection<Feature> _features;
        private ObservableCollection<Feature> _filteredFeatures;
        private int _implementedCount;
        private int _partialCount;
        private int _designedCount;
        private int _inProgressCount;
        private string _searchText = string.Empty;
        private FeatureStatus? _statusFilter = null;
        private bool _isScanning;
        
        private readonly FeatureScannerService _scanner;
        private FileSystemWatcher? _kdsWatcher;

        public FeaturesViewModel()
        {
            _features = new ObservableCollection<Feature>();
            _filteredFeatures = new ObservableCollection<Feature>();
            
            // Initialize commands first (must be non-null)
            RefreshCommand = new RelayCommand(_ => ExecuteRefresh());
            ClearFiltersCommand = new RelayCommand(_ => ExecuteClearFilters());
            
            try
            {
                // Initialize scanner with KDS root path
                var kdsPath = Helpers.ConfigurationHelper.GetKdsRoot();
                _scanner = new FeatureScannerService(kdsPath);
                
                // Set up FileSystemWatcher for auto-refresh on kds.md changes
                SetupFileWatcher(kdsPath);
                
                // Initial load
                LoadFeatures();
                
                ErrorViewModel.Instance.LogInfo("FeaturesViewModel", 
                    $"Feature scanning initialized - Found {Features.Count} features");
            }
            catch (Exception ex)
            {
                // Initialize with empty scanner on error
                var fallbackPath = @"D:\PROJECTS\KDS";
                _scanner = new FeatureScannerService(fallbackPath);
                
                ErrorViewModel.Instance.LogError("FeaturesViewModel", 
                    "Error initializing FeaturesViewModel", ex);
            }
        }

        #region Properties

        public ObservableCollection<Feature> Features
        {
            get => _features;
            set => SetProperty(ref _features, value);
        }

        public ObservableCollection<Feature> FilteredFeatures
        {
            get => _filteredFeatures;
            set => SetProperty(ref _filteredFeatures, value);
        }

        public int ImplementedCount
        {
            get => _implementedCount;
            set => SetProperty(ref _implementedCount, value);
        }

        public int PartialCount
        {
            get => _partialCount;
            set => SetProperty(ref _partialCount, value);
        }

        public int DesignedCount
        {
            get => _designedCount;
            set => SetProperty(ref _designedCount, value);
        }

        public int InProgressCount
        {
            get => _inProgressCount;
            set => SetProperty(ref _inProgressCount, value);
        }

        public string SearchText
        {
            get => _searchText;
            set
            {
                if (SetProperty(ref _searchText, value))
                {
                    ApplyFilters();
                }
            }
        }

        public FeatureStatus? StatusFilter
        {
            get => _statusFilter;
            set
            {
                if (SetProperty(ref _statusFilter, value))
                {
                    ApplyFilters();
                }
            }
        }

        public bool IsScanning
        {
            get => _isScanning;
            set => SetProperty(ref _isScanning, value);
        }

        #endregion

        #region Commands

        public ICommand RefreshCommand { get; }
        public ICommand ClearFiltersCommand { get; }

        private void ExecuteRefresh()
        {
            LoadFeatures(forceRefresh: true);
        }

        private void ExecuteClearFilters()
        {
            SearchText = string.Empty;
            StatusFilter = null;
        }

        #endregion

        #region Methods

        private void LoadFeatures(bool forceRefresh = false)
        {
            IsScanning = true;

            try
            {
                // Scan features using FeatureScannerService
                var scannedFeatures = _scanner.ScanFeatures(forceRefresh);
                
                // Update observable collection
                Features.Clear();
                foreach (var feature in scannedFeatures.OrderBy(f => f.Name))
                {
                    Features.Add(feature);
                }

                // Update counts
                ImplementedCount = Features.Count(f => f.Status == FeatureStatus.FullyImplemented);
                PartialCount = Features.Count(f => f.Status == FeatureStatus.PartiallyImplemented);
                DesignedCount = Features.Count(f => f.Status == FeatureStatus.DesignedOnly);
                InProgressCount = Features.Count(f => f.Status == FeatureStatus.InProgress);

                // Apply filters
                ApplyFilters();

                ErrorViewModel.Instance.LogInfo("FeaturesViewModel", 
                    $"Feature scan complete: {Features.Count} features " +
                    $"(✅ {ImplementedCount}, 🟡 {PartialCount}, 🔄 {InProgressCount}, 📋 {DesignedCount})");
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("FeaturesViewModel", 
                    "Error loading features", ex);
            }
            finally
            {
                IsScanning = false;
            }
        }

        private void ApplyFilters()
        {
            var filtered = Features.AsEnumerable();

            // Apply search filter
            if (!string.IsNullOrWhiteSpace(SearchText))
            {
                var searchLower = SearchText.ToLower();
                filtered = filtered.Where(f => 
                    f.Name.ToLower().Contains(searchLower) ||
                    f.Notes.ToLower().Contains(searchLower) ||
                    f.MissingComponentsText.ToLower().Contains(searchLower));
            }

            // Apply status filter
            if (StatusFilter.HasValue)
            {
                filtered = filtered.Where(f => f.Status == StatusFilter.Value);
            }

            // Update filtered collection
            FilteredFeatures.Clear();
            foreach (var feature in filtered)
            {
                FilteredFeatures.Add(feature);
            }
        }

        private void SetupFileWatcher(string kdsPath)
        {
            try
            {
                var kdsDocPath = Path.Combine(kdsPath, "prompts", "user", "kds.md");
                if (!File.Exists(kdsDocPath))
                    return;

                _kdsWatcher = new FileSystemWatcher
                {
                    Path = Path.GetDirectoryName(kdsDocPath)!,
                    Filter = "kds.md",
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size
                };

                _kdsWatcher.Changed += (s, e) =>
                {
                    // Debounce: wait 500ms before reloading
                    System.Threading.Thread.Sleep(500);
                    
                    System.Windows.Application.Current?.Dispatcher.Invoke(() =>
                    {
                        LoadFeatures(forceRefresh: true);
                    });
                };

                _kdsWatcher.EnableRaisingEvents = true;
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("FeaturesViewModel", 
                    "Error setting up FileSystemWatcher", ex);
            }
        }

        #endregion

        #region Disposal

        public void Dispose()
        {
            _kdsWatcher?.Dispose();
        }

        #endregion
    }
}
