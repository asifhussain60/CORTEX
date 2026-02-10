namespace TestSolution.Core.Entities
{
    public interface IEntity
    {
        int Id { get; set; }
    }

    public class User : IEntity
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        
        public string GetDisplayName()
        {
            return $"User: {Name}";
        }
    }
}
