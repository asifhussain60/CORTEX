using System.Windows.Controls;
using KDS.Dashboard.WPF.ViewModels;

namespace KDS.Dashboard.WPF.Views
{
    public partial class DashboardView : UserControl
    {
        public DashboardView()
        {
            InitializeComponent();
            DataContext = new DashboardViewModel();
        }
    }
}
