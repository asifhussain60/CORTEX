using System;
using System.Globalization;
using System.Windows.Data;
using System.Windows.Media;

namespace KDS.Dashboard.WPF.Converters
{
    /// <summary>
    /// Converts result status strings (GREEN, COMPLETE, VALIDATED, etc.) to appropriate colors
    /// </summary>
    public class ResultToColorConverter : IValueConverter
    {
        private static readonly SolidColorBrush GreenBrush = new(Color.FromRgb(46, 125, 50)); // #2E7D32
        private static readonly SolidColorBrush RedBrush = new(Color.FromRgb(198, 40, 40)); // #C62828
        private static readonly SolidColorBrush BlueBrush = new(Color.FromRgb(25, 118, 210)); // #1976D2
        private static readonly SolidColorBrush OrangeBrush = new(Color.FromRgb(245, 124, 0)); // #F57C00
        private static readonly SolidColorBrush GrayBrush = new(Color.FromRgb(158, 158, 158)); // #9E9E9E

        public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is not string result || string.IsNullOrWhiteSpace(result))
            {
                return GrayBrush;
            }

            return result.ToUpperInvariant() switch
            {
                "GREEN" or "COMPLETE" or "VALIDATED" => GreenBrush,
                "RED" or "FAILED" => RedBrush,
                "REFACTOR" or "IN_PROGRESS" => BlueBrush,
                "WARNING" => OrangeBrush,
                _ => GrayBrush
            };
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException("ConvertBack is not supported for ResultToColorConverter");
        }
    }
}
