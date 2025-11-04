namespace KDS.Tests.Fixtures
{
    // Sample implementation file (created during GREEN phase)
    // This file would NOT exist during RED phase
    
    /// <summary>
    /// Sample button component for TDD cycle validation
    /// </summary>
    public class SampleButton
    {
        /// <summary>
        /// Gets or sets the button label
        /// </summary>
        public string Label { get; set; }
        
        /// <summary>
        /// Gets whether the button has been clicked
        /// </summary>
        public bool IsClicked { get; private set; }
        
        /// <summary>
        /// Initializes a new instance of the SampleButton class
        /// </summary>
        /// <param name="label">Button label</param>
        public SampleButton(string label)
        {
            Label = label;
            IsClicked = false;
        }
        
        /// <summary>
        /// Simulates clicking the button
        /// </summary>
        public void Click()
        {
            IsClicked = true;
        }
    }
}
