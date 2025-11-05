using System;
using System.Collections.ObjectModel;
using System.Linq;
using KDS.Dashboard.WPF.Models;

namespace KDS.Dashboard.WPF.ViewModels
{
    /// <summary>
    /// ViewModel for the Features tab showing feature inventory
    /// Placeholder for Phase 2 - will scan brain files for features
    /// </summary>
    public class FeaturesViewModel : ViewModelBase
    {
        private ObservableCollection<Feature> _features;
        private int _implementedCount;
        private int _partialCount;
        private int _designedCount;

        public FeaturesViewModel()
        {
            _features = new ObservableCollection<Feature>();
            
            try
            {
                LoadFeatures();
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("FeaturesViewModel", 
                    "Error initializing FeaturesViewModel", ex);
            }
        }

        public ObservableCollection<Feature> Features
        {
            get => _features;
            set => SetProperty(ref _features, value);
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

        private void LoadFeatures()
        {
            // TODO Phase 2: Implement feature scanning from brain files
            // For now, return empty collection
            ErrorViewModel.Instance.LogInfo("FeaturesViewModel", 
                "Feature scanning not yet implemented - Phase 2 task");
            
            Features = new ObservableCollection<Feature>();
            ImplementedCount = 0;
            PartialCount = 0;
            DesignedCount = 0;
        }
    }
}
