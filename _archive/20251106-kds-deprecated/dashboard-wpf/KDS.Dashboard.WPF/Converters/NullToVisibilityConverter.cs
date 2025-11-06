using System;
using System.Globalization;
using System.Windows;
using System.Windows.Data;

namespace KDS.Dashboard.WPF.Converters
{
    /// <summary>
    /// Converts null or empty collections to Visibility.Collapsed, otherwise Visibility.Visible
    /// </summary>
    public class NullToVisibilityConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value == null)
                return Visibility.Collapsed;

            if (value is string str && string.IsNullOrWhiteSpace(str))
                return Visibility.Collapsed;

            if (value is System.Collections.IEnumerable enumerable)
            {
                var enumerator = enumerable.GetEnumerator();
                bool hasItems = enumerator.MoveNext();
                if (enumerator is IDisposable disposable)
                    disposable.Dispose();
                return hasItems ? Visibility.Visible : Visibility.Collapsed;
            }

            return Visibility.Visible;
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
}
