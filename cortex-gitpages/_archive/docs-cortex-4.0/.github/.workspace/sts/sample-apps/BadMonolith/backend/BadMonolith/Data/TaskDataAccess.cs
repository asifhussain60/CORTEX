using Microsoft.Data.SqlClient;
using System.Collections.Generic;

namespace BadMonolith.Data
{
    /// <summary>
    /// Task data access demonstrating data layer anti-patterns.
    /// 
    /// Anti-patterns demonstrated:
    /// ❌ No abstraction or repository pattern
    /// ❌ Direct SqlConnection usage
    /// ❌ Repeated connection code
    /// ❌ No ORM usage (Entity Framework)
    /// ❌ String concatenation for queries
    /// ❌ No query builder or stored procedures
    /// </summary>
    public class TaskDataAccess
    {
        private string _connectionString;

        public TaskDataAccess(string connectionString)
        {
            _connectionString = connectionString;
        }

        // ❌ FLAW: Duplicated connection code (repeated everywhere)
        public List<Dictionary<string, object>> GetAllTasks()
        {
            var tasks = new List<Dictionary<string, object>>();
            
            using (var conn = new SqlConnection(_connectionString))
            {
                conn.Open();
                var cmd = conn.CreateCommand();
                // ❌ FLAW: No LIMIT, no OFFSET
                // Returns all results - potential for millions of rows
                cmd.CommandText = "SELECT Id, Title, IsCompleted FROM Tasks ORDER BY Id";
                
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        tasks.Add(new Dictionary<string, object>
                        {
                            ["Id"] = reader.GetInt32(0),
                            ["Title"] = reader.GetString(1),
                            ["IsCompleted"] = reader.GetBoolean(2)
                        });
                    }
                }
            }
            
            return tasks;
        }

        // ❌ FLAW: No pagination support
        // ❌ FLAW: Unbounded result set
        public List<Dictionary<string, object>> GetAllTasksUnbounded()
        {
            var tasks = new List<Dictionary<string, object>>();
            
            using (var conn = new SqlConnection(_connectionString))
            {
                conn.Open();
                var cmd = conn.CreateCommand();
                // ❌ FLAW: No LIMIT clause at all
                cmd.CommandText = "SELECT * FROM Tasks";
                
                using (var reader = cmd.ExecuteReader())
                {
                    // ❌ FLAW: No result count limit
                    // Infinite loop possible if table is huge
                    while (reader.Read())
                    {
                        var task = new Dictionary<string, object>();
                        for (int i = 0; i < reader.FieldCount; i++)
                        {
                            task[reader.GetName(i)] = reader.GetValue(i);
                        }
                        tasks.Add(task);
                    }
                }
            }
            
            return tasks;
        }

        // ❌ FLAW: Separate method for single task (duplicated logic)
        public Dictionary<string, object> GetTaskById(int id)
        {
            // ❌ FLAW: Duplicated connection setup code
            using (var conn = new SqlConnection(_connectionString))
            {
                conn.Open();
                var cmd = conn.CreateCommand();
                // ❌ FLAW: String concatenation - SQL injection
                cmd.CommandText = $"SELECT Id, Title, IsCompleted FROM Tasks WHERE Id = {id}";
                
                using (var reader = cmd.ExecuteReader())
                {
                    if (reader.Read())
                    {
                        return new Dictionary<string, object>
                        {
                            ["Id"] = reader.GetInt32(0),
                            ["Title"] = reader.GetString(1),
                            ["IsCompleted"] = reader.GetBoolean(2)
                        };
                    }
                }
            }
            
            // ❌ FLAW: Returns null instead of throwing or using Optional
            return null;
        }

        // ❌ FLAW: Create method duplicates connection code again
        public void CreateTask(string title)
        {
            // ❌ FLAW: Third time we're writing connection code
            using (var conn = new SqlConnection(_connectionString))
            {
                conn.Open();
                var cmd = conn.CreateCommand();
                // ❌ FLAW: String interpolation (SQL injection)
                cmd.CommandText = $"INSERT INTO Tasks(Title, IsCompleted) VALUES('{title}', 0)";
                // ❌ FLAW: No return value check (ExecuteNonQuery)
                cmd.ExecuteNonQuery();
            }
        }

        // ❌ FLAW: No connection pooling awareness
        // ❌ FLAW: No async/await patterns
        // ❌ FLAW: No transaction support
        // ❌ FLAW: No query optimization
        // ❌ FLAW: Missing indexes on WHERE clauses
    }
}
