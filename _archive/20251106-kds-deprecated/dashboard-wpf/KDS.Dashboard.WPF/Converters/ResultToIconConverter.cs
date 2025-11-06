using System;
using System.Globalization;
using System.Windows.Data;
using MaterialDesignThemes.Wpf;

namespace KDS.Dashboard.WPF.Converters
{
    /// <summary>
    /// Converts result status strings (GREEN, COMPLETE, VALIDATED, etc.) to Material Design icons
    /// </summary>
    public class ResultToIconConverter : IValueConverter
    {
        public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is not string result || string.IsNullOrWhiteSpace(result))
            {
                return PackIconKind.HelpCircle;
            }

            return result.ToUpperInvariant() switch
            {
                "GREEN" => PackIconKind.CheckCircle,
                "COMPLETE" => PackIconKind.Check,
                "VALIDATED" => PackIconKind.ShieldCheck,
                "RED" => PackIconKind.AlertCircle,
                "FAILED" => PackIconKind.CloseCircle,
                "REFACTOR" => PackIconKind.AutoFix,
                "IN_PROGRESS" => PackIconKind.ProgressClock,
                "WARNING" => PackIconKind.Alert,
                _ => PackIconKind.HelpCircle
            };
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException("ConvertBack is not supported for ResultToIconConverter");
        }
    }
}
