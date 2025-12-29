/**
 * CORTEX Design Patterns Data
 * Complete Gang of Four + Enterprise patterns database
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

const PATTERNS_DATA = {
    // ============================================
    // CREATIONAL PATTERNS (5)
    // ============================================
    'singleton': {
        name: 'Singleton',
        type: 'creational',
        intent: 'Ensure a class only has one instance and provide a global point of access to it.',
        problem: 'You need exactly one instance of a class, accessible globally, without allowing multiple instances.',
        solution: 'Make the constructor private, store the instance in a static field, and provide a static method to get the instance.',
        useCases: [
            'Managing database connection pools',
            'Caching frequently accessed data',
            'Application configuration settings',
            'Logging service',
            'Resource management (hardware, external connections)'
        ],
        consequences: {
            positive: [
                'Strict control over instance access',
                'Better than global variables (no namespace pollution)',
                'Can be subclassed with protected constructor',
                'Easy to switch to multiple instances if needed'
            ],
            negative: [
                'Violates Single Responsibility Principle (controls creation AND lifecycle)',
                'Can make unit testing difficult',
                'Often overused - consider DI container instead'
            ]
        },
        relatedPatterns: ['Abstract Factory', 'Builder', 'Prototype', 'State'],
        codeExample: `// Thread-safe Singleton with Lazy<T>
public class Logger
{
    private static readonly Lazy<Logger> _lazyLogger = 
        new Lazy<Logger>(() => new Logger());
    
    public static Logger Instance => _lazyLogger.Value;
    
    protected Logger() { }
    
    public void Log(string message)
    {
        Console.WriteLine($"[{DateTime.Now}] {message}");
    }
}

// Usage
Logger.Instance.Log("Application started");`,
        cortexUsage: 'CORTEX uses Singleton for conversation context management and brain state persistence. Consider for services requiring exactly one instance with global access.'
    },

    'factory-method': {
        name: 'Factory Method',
        type: 'creational',
        intent: 'Define an interface for creating an object, but let subclasses decide which class to instantiate.',
        problem: 'You need to create objects without specifying the exact class, allowing subclasses to alter the type of objects created.',
        solution: 'Define a factory method in a base class that returns a product interface. Subclasses override this method to create specific products.',
        useCases: [
            'When a class cannot anticipate the class of objects it must create',
            'When subclasses should specify the objects they create',
            'Creating objects that share a common interface but have different implementations',
            'Plugin architectures'
        ],
        consequences: {
            positive: [
                'Eliminates tight coupling between creator and concrete products',
                'Adheres to Open/Closed Principle',
                'Adheres to Single Responsibility Principle'
            ],
            negative: [
                'May require creating subclass just for one product type',
                'Can add complexity for simple object creation'
            ]
        },
        relatedPatterns: ['Abstract Factory', 'Prototype', 'Template Method'],
        codeExample: `// Product interface
public interface IDiscountService
{
    decimal DiscountPercentage { get; }
}

// Concrete products
public class CountryDiscountService : IDiscountService
{
    public decimal DiscountPercentage => 
        _country == "Belgium" ? 0.20m : 0.10m;
    
    private readonly string _country;
    public CountryDiscountService(string country) => _country = country;
}

// Creator (Factory)
public abstract class DiscountFactory
{
    public abstract IDiscountService CreateDiscountService();
}

// Concrete Creator
public class CountryDiscountFactory : DiscountFactory
{
    private readonly string _country;
    public CountryDiscountFactory(string country) => _country = country;
    
    public override IDiscountService CreateDiscountService()
        => new CountryDiscountService(_country);
}`,
        cortexUsage: 'CORTEX uses Factory Method for creating orchestrator instances and response formatters. Use when object creation logic needs to vary independently.'
    },

    'abstract-factory': {
        name: 'Abstract Factory',
        type: 'creational',
        intent: 'Provide an interface for creating families of related or dependent objects without specifying their concrete classes.',
        problem: 'You need to create multiple related objects that belong together as a family, ensuring compatibility.',
        solution: 'Define an abstract factory interface with methods for each product type. Concrete factories implement these methods to create specific product families.',
        useCases: [
            'Supporting multiple UI themes/styles',
            'Cross-platform development (Windows/Mac/Linux components)',
            'Database abstraction (SQL Server/MySQL/PostgreSQL)',
            'Document conversion (multiple input/output formats)',
            'Multi-tenant applications with tenant-specific configurations'
        ],
        consequences: {
            positive: [
                'Isolates concrete classes from client',
                'Easy to exchange product families',
                'Promotes consistency among products',
                'Adheres to Open/Closed Principle'
            ],
            negative: [
                'Adding new product types requires interface changes',
                'Can become complex with many product types'
            ]
        },
        relatedPatterns: ['Factory Method', 'Prototype', 'Singleton'],
        codeExample: `// Abstract products
public interface IDiscountService { decimal DiscountPercentage { get; } }
public interface IShippingService { decimal ShippingCosts { get; } }

// Abstract factory
public interface IShoppingCartFactory
{
    IDiscountService CreateDiscountService();
    IShippingService CreateShippingService();
}

// Concrete factory for Belgium
public class BelgiumFactory : IShoppingCartFactory
{
    public IDiscountService CreateDiscountService() 
        => new BelgiumDiscountService();
    public IShippingService CreateShippingService() 
        => new BelgiumShippingService();
}

// Client uses factory, not concrete classes
public class ShoppingCart
{
    private readonly IDiscountService _discount;
    private readonly IShippingService _shipping;
    
    public ShoppingCart(IShoppingCartFactory factory)
    {
        _discount = factory.CreateDiscountService();
        _shipping = factory.CreateShippingService();
    }
}`,
        cortexUsage: 'CORTEX uses Abstract Factory for creating brain tier configurations and template rendering systems. Use when you need families of related objects that work together.'
    },

    'builder': {
        name: 'Builder',
        type: 'creational',
        intent: 'Separate the construction of a complex object from its representation so the same construction process can create different representations.',
        problem: 'You need to construct complex objects step by step, with the ability to produce different types and representations.',
        solution: 'Extract object construction code into separate builder classes. A director controls the building steps, while concrete builders define how each step is implemented.',
        useCases: [
            'Generating documents (PDFs, reports)',
            'Building database queries',
            'Game character creation with customizable attributes',
            'Constructing UI forms with various fields',
            'Email message composition'
        ],
        consequences: {
            positive: [
                'Construct objects step by step',
                'Reuse construction code for different representations',
                'Isolates complex construction code (SRP)',
                'Finer control over construction process'
            ],
            negative: [
                'Increases code complexity with multiple new classes',
                'May be overkill for simple objects'
            ]
        },
        relatedPatterns: ['Abstract Factory', 'Composite', 'Singleton'],
        codeExample: `// Product
public class Car
{
    public List<string> Parts { get; } = new();
    public void AddPart(string part) => Parts.Add(part);
}

// Builder
public abstract class CarBuilder
{
    public Car Car { get; protected set; }
    protected CarBuilder(string type) => Car = new Car();
    
    public abstract void BuildEngine();
    public abstract void BuildFrame();
}

// Concrete Builder
public class BMWBuilder : CarBuilder
{
    public BMWBuilder() : base("BMW") { }
    public override void BuildEngine() => Car.AddPart("BMW V8 Engine");
    public override void BuildFrame() => Car.AddPart("BMW Sport Frame");
}

// Director
public class Garage
{
    public void Construct(CarBuilder builder)
    {
        builder.BuildFrame();
        builder.BuildEngine();
    }
}`,
        cortexUsage: 'CORTEX uses Builder for constructing complex response templates and planning documents. Use for objects requiring multiple construction steps with different configurations.'
    },

    'prototype': {
        name: 'Prototype',
        type: 'creational',
        intent: 'Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype.',
        problem: 'You need to copy existing objects without making code dependent on their classes, or creating from scratch is expensive.',
        solution: 'Implement a Clone method on objects that returns a copy. Support both shallow (primitive values) and deep copies (complex nested objects).',
        useCases: [
            'Document cloning in word processors',
            'Managing configuration instances',
            'Creating reusable UI component templates',
            'Game entity/character creation',
            'Caching expensive-to-create objects'
        ],
        consequences: {
            positive: [
                'Hides concrete product classes from client',
                'Reduced subclassing compared to Factory Method',
                'Can add/remove products at runtime',
                'Configure application with prototypes'
            ],
            negative: [
                'Each class must implement Clone method',
                'Deep copying complex objects can be tricky',
                'Circular references need special handling'
            ]
        },
        relatedPatterns: ['Abstract Factory', 'Factory Method', 'Singleton', 'Composite', 'Decorator'],
        codeExample: `public abstract class Person
{
    public string Name { get; set; }
    public abstract Person Clone(bool deepClone = false);
}

public class Employee : Person
{
    public Manager Manager { get; set; }
    
    public override Person Clone(bool deepClone = false)
    {
        if (deepClone)
        {
            // Deep clone using JSON serialization
            var json = JsonSerializer.Serialize(this);
            return JsonSerializer.Deserialize<Employee>(json);
        }
        // Shallow clone
        return (Employee)MemberwiseClone();
    }
}`,
        cortexUsage: 'CORTEX uses Prototype for cloning context objects and creating variations of planning templates. Use when copying existing objects is more efficient than creating new ones.'
    },

    // ============================================
    // STRUCTURAL PATTERNS (7)
    // ============================================
    'adapter': {
        name: 'Adapter',
        type: 'structural',
        intent: 'Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn\'t otherwise because of incompatible interfaces.',
        problem: 'You have existing code with one interface but need to use it with code expecting a different interface.',
        solution: 'Create an adapter class that wraps the original class and translates calls between the incompatible interfaces.',
        useCases: [
            'Integrating third-party libraries',
            'Connecting to external web services',
            'Mocking objects for testing',
            'Integrating logging/monitoring frameworks',
            'Legacy system integration'
        ],
        consequences: {
            positive: [
                'Single adapter works with adaptee and all subclasses',
                'Separates interface adaptation from business logic (SRP)',
                'New adapters can be added without changing client (OCP)',
                'Can add functionality to all adaptees at once'
            ],
            negative: [
                'Object adapter makes overriding adaptee behavior harder',
                'Adds extra layer of indirection'
            ]
        },
        relatedPatterns: ['Bridge', 'Decorator', 'Facade', 'Proxy'],
        codeExample: `// External system with incompatible interface
public class ExternalSystem
{
    public CityFromExternal GetCity() 
        => new CityFromExternal("Antwerp", "Stad", 500000);
}

// Target interface our code expects
public interface ICityAdapter
{
    City GetCity();
}

// Adapter (Object Adapter - composition)
public class CityAdapter : ICityAdapter
{
    private readonly ExternalSystem _external = new();
    
    public City GetCity()
    {
        var external = _external.GetCity();
        return new City
        {
            FullName = $"{external.Name} ({external.NickName})",
            Inhabitants = external.Inhabitants
        };
    }
}`,
        cortexUsage: 'CORTEX uses Adapter extensively for integrating external APIs and normalizing data from different sources. Essential for any external system integration.'
    },

    'bridge': {
        name: 'Bridge',
        type: 'structural',
        intent: 'Decouple an abstraction from its implementation so the two can vary independently.',
        problem: 'You want to avoid a permanent binding between abstraction and implementation, especially when both need to be extended.',
        solution: 'Separate the abstraction hierarchy from the implementation hierarchy. The abstraction holds a reference to an implementor.',
        useCases: [
            'Separating notification mechanisms (email/SMS/push) from notification logic',
            'Audio/video streaming protocols separate from player logic',
            'UI components separate from platform-specific rendering',
            'Universal remote control systems',
            'Database drivers'
        ],
        consequences: {
            positive: [
                'Decoupling: implementation can change at runtime',
                'Improved extensibility: extend hierarchies independently',
                'Hide implementation details from clients',
                'Adheres to OCP and SRP'
            ],
            negative: [
                'Increased complexity with additional classes',
                'May be overkill for simple variations'
            ]
        },
        relatedPatterns: ['Abstract Factory', 'Adapter', 'Strategy'],
        codeExample: `// Implementor
public interface ICoupon
{
    int CouponValue { get; }
}

public class TwoEuroCoupon : ICoupon
{
    public int CouponValue => 2;
}

// Abstraction
public abstract class Menu
{
    protected readonly ICoupon _coupon;
    protected Menu(ICoupon coupon) => _coupon = coupon;
    public abstract decimal CalculatePrice();
}

// Refined Abstraction
public class VegetarianMenu : Menu
{
    public VegetarianMenu(ICoupon coupon) : base(coupon) { }
    
    public override decimal CalculatePrice()
        => 15.00m - _coupon.CouponValue;
}

// Usage: Both can vary independently
var menu = new VegetarianMenu(new TwoEuroCoupon());`,
        cortexUsage: 'CORTEX uses Bridge for separating response formatting from content generation. Use when you need two dimensions of variation that shouldn\'t create an explosion of classes.'
    },

    'composite': {
        name: 'Composite',
        type: 'structural',
        intent: 'Compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions uniformly.',
        problem: 'You need to work with tree-like structures where clients should treat single objects and compositions the same way.',
        solution: 'Define a component interface implemented by both leaf nodes (no children) and composite nodes (contain children). Composites delegate operations to children.',
        useCases: [
            'File system representation',
            'XML/HTML document structures',
            'Organization charts',
            'Menu systems with submenus',
            'Drawing applications (shapes containing shapes)',
            'Investment portfolios'
        ],
        consequences: {
            positive: [
                'Clients treat leaves and composites uniformly (simple client code)',
                'Easy to add new component types (OCP)',
                'Recursive operations are natural'
            ],
            negative: [
                'Can make system too generic',
                'Hard to restrict composite contents (type checking at runtime)'
            ]
        },
        relatedPatterns: ['Chain of Responsibility', 'Decorator', 'Iterator', 'Visitor'],
        codeExample: `// Component
public abstract class FileSystemItem
{
    public string Name { get; }
    protected FileSystemItem(string name) => Name = name;
    public abstract long GetSize();
}

// Leaf
public class File : FileSystemItem
{
    private readonly long _size;
    public File(string name, long size) : base(name) => _size = size;
    public override long GetSize() => _size;
}

// Composite
public class Directory : FileSystemItem
{
    private readonly List<FileSystemItem> _items = new();
    private readonly long _size;
    
    public Directory(string name, long size) : base(name) => _size = size;
    
    public void Add(FileSystemItem item) => _items.Add(item);
    
    public override long GetSize()
        => _size + _items.Sum(item => item.GetSize()); // Recursive!
}`,
        cortexUsage: 'CORTEX uses Composite for representing hierarchical document structures and nested planning components. Essential for any tree-like data representation.'
    },

    'decorator': {
        name: 'Decorator',
        type: 'structural',
        intent: 'Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.',
        problem: 'You need to add behavior to objects at runtime without affecting other objects of the same class.',
        solution: 'Create decorator classes that wrap the original object, implementing the same interface and adding behavior before/after delegating to the wrapped object.',
        useCases: [
            'Adding logging and monitoring capabilities',
            'Text formatting in editors (bold, italic, underline)',
            'Adding authentication/authorization layers',
            'Styling/theming UI components',
            'Stream processing (buffering, compression, encryption)'
        ],
        consequences: {
            positive: [
                'More flexible than static inheritance',
                'Add/remove responsibilities at runtime',
                'Avoids feature-loaded classes (SRP)',
                'Can combine multiple decorators'
            ],
            negative: [
                'Lots of small similar classes',
                'Order of decoration can matter',
                'Hard to remove specific decorator from stack'
            ]
        },
        relatedPatterns: ['Adapter', 'Composite', 'Strategy'],
        codeExample: `// Component
public interface IMailService
{
    bool SendMail(string message);
}

public class CloudMailService : IMailService
{
    public bool SendMail(string message)
    {
        Console.WriteLine($"Sending via cloud: {message}");
        return true;
    }
}

// Base Decorator
public abstract class MailServiceDecorator : IMailService
{
    protected readonly IMailService _mailService;
    protected MailServiceDecorator(IMailService service) 
        => _mailService = service;
    
    public virtual bool SendMail(string message) 
        => _mailService.SendMail(message);
}

// Concrete Decorator
public class StatisticsDecorator : MailServiceDecorator
{
    public StatisticsDecorator(IMailService service) : base(service) { }
    
    public override bool SendMail(string message)
    {
        var start = DateTime.Now;
        var result = base.SendMail(message);
        Console.WriteLine($"Time: {DateTime.Now - start}");
        return result;
    }
}`,
        cortexUsage: 'CORTEX uses Decorator for adding cross-cutting concerns like logging, timing, and validation to core services. Use when you need to add behavior without modifying existing code.'
    },

    'facade': {
        name: 'Facade',
        type: 'structural',
        intent: 'Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use.',
        problem: 'A complex subsystem has many interfaces that clients find difficult to use correctly.',
        solution: 'Create a facade class that provides a simple interface to the complex subsystem, delegating client requests to appropriate subsystem objects.',
        useCases: [
            'Simplifying complex library APIs',
            'Layered architecture (service layer)',
            'Third-party integration wrappers',
            'Legacy system modernization',
            'Unified API for microservices'
        ],
        consequences: {
            positive: [
                'Isolates clients from subsystem complexity',
                'Promotes weak coupling',
                'Doesn\'t prevent direct subsystem access if needed'
            ],
            negative: [
                'Facade can become a "god object" if overused',
                'May hide useful subsystem features'
            ]
        },
        relatedPatterns: ['Abstract Factory', 'Mediator', 'Singleton'],
        codeExample: `// Complex subsystem classes
public class DiscountService { ... }
public class ShippingService { ... }
public class PaymentService { ... }
public class InventoryService { ... }

// Facade simplifies the complex subsystem
public class OrderFacade
{
    private readonly DiscountService _discount = new();
    private readonly ShippingService _shipping = new();
    private readonly PaymentService _payment = new();
    private readonly InventoryService _inventory = new();
    
    public OrderResult PlaceOrder(Order order)
    {
        // Coordinates all subsystems
        var discount = _discount.Calculate(order);
        var shipping = _shipping.Calculate(order);
        
        if (!_inventory.CheckAvailability(order))
            return OrderResult.OutOfStock;
            
        var total = order.Subtotal - discount + shipping;
        
        if (!_payment.Process(order.PaymentInfo, total))
            return OrderResult.PaymentFailed;
            
        _inventory.Reserve(order);
        return OrderResult.Success;
    }
}`,
        cortexUsage: 'CORTEX provides facades for complex orchestration operations. The CLI commands are facades over complex multi-step processes. Use to simplify complex subsystem interactions.'
    },

    'flyweight': {
        name: 'Flyweight',
        type: 'structural',
        intent: 'Use sharing to support large numbers of fine-grained objects efficiently.',
        problem: 'You need to create a huge number of similar objects, causing memory issues.',
        solution: 'Share common state (intrinsic) among objects. Store unique state (extrinsic) externally and pass it to flyweight methods.',
        useCases: [
            'Text editors (character formatting)',
            'Game development (particles, trees, terrain)',
            'Caching identical objects',
            'Browser DOM optimization',
            'Icon/image libraries'
        ],
        consequences: {
            positive: [
                'Reduces memory usage significantly',
                'Centralizes state management'
            ],
            negative: [
                'Adds complexity',
                'Trading memory for CPU (computing extrinsic state)',
                'Code becomes harder to understand'
            ]
        },
        relatedPatterns: ['Composite', 'State', 'Strategy'],
        codeExample: `// Flyweight stores shared (intrinsic) state
public class TreeType
{
    public string Name { get; }
    public string Color { get; }
    public string Texture { get; }
    
    public TreeType(string name, string color, string texture)
    {
        Name = name; Color = color; Texture = texture;
    }
    
    public void Draw(int x, int y) // Extrinsic state passed in
    {
        Console.WriteLine($"Drawing {Name} tree at ({x},{y})");
    }
}

// Flyweight Factory
public class TreeFactory
{
    private static Dictionary<string, TreeType> _treeTypes = new();
    
    public static TreeType GetTreeType(string name, string color, string texture)
    {
        var key = $"{name}_{color}_{texture}";
        if (!_treeTypes.ContainsKey(key))
            _treeTypes[key] = new TreeType(name, color, texture);
        return _treeTypes[key];
    }
}`,
        cortexUsage: 'CORTEX uses Flyweight for caching frequently accessed knowledge patterns and reusing template components. Use when you need many similar objects with shared state.'
    },

    'proxy': {
        name: 'Proxy',
        type: 'structural',
        intent: 'Provide a surrogate or placeholder for another object to control access to it.',
        problem: 'You need to control access to an object, add functionality before/after accessing it, or defer expensive operations.',
        solution: 'Create a proxy class with the same interface as the real object. The proxy controls access and can add behavior.',
        useCases: [
            'Lazy initialization (virtual proxy)',
            'Access control (protection proxy)',
            'Logging/caching (smart proxy)',
            'Remote object access (remote proxy)',
            'Resource-intensive object management'
        ],
        consequences: {
            positive: [
                'Control service object without clients knowing',
                'Manage lifecycle of service object',
                'Works even if service object isn\'t ready',
                'Add new proxies without changing service (OCP)'
            ],
            negative: [
                'Response might be delayed',
                'Code complexity increases'
            ]
        },
        relatedPatterns: ['Adapter', 'Decorator', 'Facade'],
        codeExample: `public interface IDocument
{
    void Display();
}

// Real expensive object
public class RealDocument : IDocument
{
    private readonly string _filename;
    
    public RealDocument(string filename)
    {
        _filename = filename;
        LoadFromDisk(); // Expensive!
    }
    
    private void LoadFromDisk() { /* Heavy operation */ }
    public void Display() => Console.WriteLine($"Displaying {_filename}");
}

// Proxy with lazy loading
public class DocumentProxy : IDocument
{
    private readonly string _filename;
    private RealDocument _realDocument;
    
    public DocumentProxy(string filename) => _filename = filename;
    
    public void Display()
    {
        _realDocument ??= new RealDocument(_filename); // Lazy init
        _realDocument.Display();
    }
}`,
        cortexUsage: 'CORTEX uses Proxy for lazy loading of large knowledge files and caching expensive operations. Essential for performance optimization with large data sets.'
    },

    // ============================================
    // BEHAVIORAL PATTERNS (11)
    // ============================================
    'chain-of-responsibility': {
        name: 'Chain of Responsibility',
        type: 'behavioral',
        intent: 'Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request.',
        problem: 'You need to process requests through a series of handlers, where each handler decides whether to process or pass along.',
        solution: 'Create a chain of handler objects. Each handler contains a reference to the next handler and decides whether to process or forward the request.',
        useCases: [
            'Middleware pipelines (ASP.NET Core)',
            'Event bubbling in UI frameworks',
            'Logging with multiple handlers',
            'Authentication/authorization chains',
            'Request validation pipelines'
        ],
        consequences: {
            positive: [
                'Reduced coupling between sender and receivers',
                'Flexibility in assigning responsibilities',
                'Easy to add/remove handlers (OCP)'
            ],
            negative: [
                'Request might go unhandled',
                'Hard to debug the flow'
            ]
        },
        relatedPatterns: ['Composite', 'Command'],
        codeExample: `public abstract class Handler
{
    protected Handler _nextHandler;
    
    public void SetNext(Handler handler) => _nextHandler = handler;
    
    public virtual void Handle(Request request)
    {
        _nextHandler?.Handle(request);
    }
}

public class AuthenticationHandler : Handler
{
    public override void Handle(Request request)
    {
        if (!request.IsAuthenticated)
        {
            Console.WriteLine("Authentication failed");
            return;
        }
        Console.WriteLine("Authentication passed");
        base.Handle(request);
    }
}

// Build chain
var auth = new AuthenticationHandler();
var validation = new ValidationHandler();
auth.SetNext(validation);
auth.Handle(request);`,
        cortexUsage: 'CORTEX uses Chain of Responsibility for its orchestrator pipeline and request processing. The brain protection rules (SKULL) use this pattern for validation chains.'
    },

    'command': {
        name: 'Command',
        type: 'behavioral',
        intent: 'Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.',
        problem: 'You need to issue requests without knowing what action will be performed or the receiver of the request.',
        solution: 'Create command objects that encapsulate all request information. Commands have an Execute method and can store state for undo.',
        useCases: [
            'Undo/Redo functionality',
            'Transaction logging',
            'Queuing and scheduling operations',
            'Macro recording',
            'GUI button/menu actions'
        ],
        consequences: {
            positive: [
                'Decouples invoker from receiver (SRP)',
                'Easy to add new commands (OCP)',
                'Can implement undo/redo',
                'Can compose commands into macros'
            ],
            negative: [
                'Can result in many command classes'
            ]
        },
        relatedPatterns: ['Composite', 'Memento', 'Prototype'],
        codeExample: `public interface ICommand
{
    void Execute();
    void Undo();
}

public class AddTextCommand : ICommand
{
    private readonly Document _doc;
    private readonly string _text;
    
    public AddTextCommand(Document doc, string text)
    {
        _doc = doc; _text = text;
    }
    
    public void Execute() => _doc.AddText(_text);
    public void Undo() => _doc.RemoveText(_text.Length);
}

// Invoker with history
public class Editor
{
    private Stack<ICommand> _history = new();
    
    public void ExecuteCommand(ICommand cmd)
    {
        cmd.Execute();
        _history.Push(cmd);
    }
    
    public void Undo()
    {
        if (_history.Count > 0)
            _history.Pop().Undo();
    }
}`,
        cortexUsage: 'CORTEX uses Command for encapsulating orchestrator operations and supporting operation history. The planning system uses commands for tracking state changes.'
    },

    'interpreter': {
        name: 'Interpreter',
        type: 'behavioral',
        intent: 'Given a language, define a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language.',
        problem: 'You need to evaluate sentences in a simple language, like configuration files or domain-specific languages.',
        solution: 'Define a class for each grammar rule. Create an abstract syntax tree of rule instances and interpret by traversing the tree.',
        useCases: [
            'SQL query parsing',
            'Regular expression engines',
            'Configuration file parsers',
            'Mathematical expression evaluators',
            'Domain-specific languages (DSLs)'
        ],
        consequences: {
            positive: [
                'Easy to change and extend grammar',
                'Implementing grammar is straightforward'
            ],
            negative: [
                'Complex grammars are hard to maintain',
                'Can be inefficient for large expressions'
            ]
        },
        relatedPatterns: ['Composite', 'Flyweight', 'Iterator', 'Visitor'],
        codeExample: `public interface IExpression
{
    int Interpret();
}

public class NumberExpression : IExpression
{
    private readonly int _number;
    public NumberExpression(int number) => _number = number;
    public int Interpret() => _number;
}

public class AddExpression : IExpression
{
    private readonly IExpression _left, _right;
    
    public AddExpression(IExpression left, IExpression right)
    {
        _left = left; _right = right;
    }
    
    public int Interpret() 
        => _left.Interpret() + _right.Interpret();
}

// Usage: 5 + 3
var expr = new AddExpression(
    new NumberExpression(5),
    new NumberExpression(3)
);
Console.WriteLine(expr.Interpret()); // 8`,
        cortexUsage: 'CORTEX uses Interpreter for parsing natural language commands and intent routing. The prompt system uses this pattern for command interpretation.'
    },

    'iterator': {
        name: 'Iterator',
        type: 'behavioral',
        intent: 'Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.',
        problem: 'You need to traverse a collection without exposing its internal structure.',
        solution: 'Define an iterator interface with methods to access elements. Collections provide iterators that know how to traverse their specific structure.',
        useCases: [
            'Traversing tree structures',
            'Database result set cursors',
            'File system directory traversal',
            'Pagination',
            'Custom collection types'
        ],
        consequences: {
            positive: [
                'Hides collection implementation (SRP)',
                'Multiple simultaneous traversals',
                'Different traversal strategies (OCP)',
                'Lazy evaluation support'
            ],
            negative: [
                'May be overkill for simple collections',
                'Less efficient than direct access'
            ]
        },
        relatedPatterns: ['Composite', 'Factory Method', 'Memento'],
        codeExample: `// In C#, IEnumerable<T> IS the iterator pattern!
public class PersonCollection : IEnumerable<Person>
{
    private List<Person> _people = new();
    
    public void Add(Person p) => _people.Add(p);
    
    public IEnumerator<Person> GetEnumerator()
    {
        foreach (var person in _people)
            yield return person; // Lazy evaluation
    }
    
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}

// Usage with foreach (uses iterator)
foreach (var person in new PersonCollection())
{
    Console.WriteLine(person.Name);
}

// LINQ uses iterators extensively
var adults = people.Where(p => p.Age >= 18);`,
        cortexUsage: 'CORTEX leverages C# built-in iterators (IEnumerable) for processing knowledge collections and search results. Use yield return for lazy evaluation of large datasets.'
    },

    'mediator': {
        name: 'Mediator',
        type: 'behavioral',
        intent: 'Define an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly.',
        problem: 'You have objects that communicate in complex ways, creating tight coupling and making the system hard to maintain.',
        solution: 'Introduce a mediator object that handles communication between objects. Objects only know about the mediator, not each other.',
        useCases: [
            'Chat room applications',
            'Air traffic control systems',
            'GUI dialog coordination',
            'Event aggregation',
            'Microservice orchestration'
        ],
        consequences: {
            positive: [
                'Reduces coupling between components',
                'Centralizes complex communications',
                'Easier to reuse individual components'
            ],
            negative: [
                'Mediator can become complex ("god object")',
                'Single point of failure'
            ]
        },
        relatedPatterns: ['Facade', 'Observer'],
        codeExample: `public interface IChatMediator
{
    void SendMessage(string message, User sender);
    void AddUser(User user);
}

public class ChatRoom : IChatMediator
{
    private List<User> _users = new();
    
    public void AddUser(User user) => _users.Add(user);
    
    public void SendMessage(string message, User sender)
    {
        foreach (var user in _users.Where(u => u != sender))
            user.Receive(message, sender.Name);
    }
}

public class User
{
    private readonly IChatMediator _mediator;
    public string Name { get; }
    
    public User(string name, IChatMediator mediator)
    {
        Name = name;
        _mediator = mediator;
        _mediator.AddUser(this);
    }
    
    public void Send(string message) => _mediator.SendMessage(message, this);
    public void Receive(string message, string from) 
        => Console.WriteLine($"{from} to {Name}: {message}");
}`,
        cortexUsage: 'CORTEX uses Mediator for coordinating between orchestrators and agents. The brain\'s corpus callosum acts as a mediator between different brain tiers.'
    },

    'memento': {
        name: 'Memento',
        type: 'behavioral',
        intent: 'Without violating encapsulation, capture and externalize an object\'s internal state so that the object can be restored to this state later.',
        problem: 'You need to save and restore an object\'s state (for undo, checkpoints, etc.) without exposing its internal structure.',
        solution: 'The originator creates memento objects containing snapshots of its state. A caretaker stores mementos but cannot modify them.',
        useCases: [
            'Undo mechanisms',
            'Game save states',
            'Transaction rollback',
            'Checkpoint/restore functionality',
            'Version history'
        ],
        consequences: {
            positive: [
                'Preserves encapsulation',
                'Simplifies originator (state management elsewhere)'
            ],
            negative: [
                'Can be memory-intensive (storing many states)',
                'Caretaker must track originator lifecycle'
            ]
        },
        relatedPatterns: ['Command', 'Iterator'],
        codeExample: `public class EditorMemento
{
    public string Content { get; }
    public int CursorPosition { get; }
    
    internal EditorMemento(string content, int cursor)
    {
        Content = content;
        CursorPosition = cursor;
    }
}

public class Editor
{
    public string Content { get; set; }
    public int CursorPosition { get; set; }
    
    public EditorMemento Save() 
        => new EditorMemento(Content, CursorPosition);
    
    public void Restore(EditorMemento memento)
    {
        Content = memento.Content;
        CursorPosition = memento.CursorPosition;
    }
}

// Caretaker
public class History
{
    private Stack<EditorMemento> _states = new();
    
    public void Push(EditorMemento memento) => _states.Push(memento);
    public EditorMemento Pop() => _states.Pop();
}`,
        cortexUsage: 'CORTEX uses Memento for brain checkpoints and conversation state snapshots. The git-checkpoint-rules.yaml defines when state should be captured.'
    },

    'observer': {
        name: 'Observer',
        type: 'behavioral',
        intent: 'Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.',
        problem: 'You need to maintain consistency between related objects without tightly coupling them.',
        solution: 'Define subject and observer interfaces. Subjects maintain a list of observers and notify them of state changes.',
        useCases: [
            'Event handling systems',
            'Model-View synchronization (MVC/MVVM)',
            'Stock price monitoring',
            'Social media notifications',
            'Real-time data feeds'
        ],
        consequences: {
            positive: [
                'Loose coupling between subject and observers',
                'Supports broadcast communication',
                'Easy to add observers (OCP)'
            ],
            negative: [
                'Observers notified in undefined order',
                'Memory leaks if observers not properly detached',
                'Can cause cascade of updates'
            ]
        },
        relatedPatterns: ['Mediator', 'Singleton'],
        codeExample: `// In C#, use events and delegates!
public class StockTicker
{
    public event EventHandler<StockChangedEventArgs> StockChanged;
    
    private decimal _price;
    public decimal Price
    {
        get => _price;
        set
        {
            if (_price != value)
            {
                _price = value;
                OnStockChanged(new StockChangedEventArgs(_price));
            }
        }
    }
    
    protected virtual void OnStockChanged(StockChangedEventArgs e)
        => StockChanged?.Invoke(this, e);
}

// Observer subscribes
var ticker = new StockTicker();
ticker.StockChanged += (sender, e) => 
    Console.WriteLine($"Price changed to: {e.Price}");`,
        cortexUsage: 'CORTEX uses Observer (via C# events) for notifying systems of context changes and brain state updates. Essential for reactive architectures.'
    },

    'state': {
        name: 'State',
        type: 'behavioral',
        intent: 'Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.',
        problem: 'An object\'s behavior depends on its state, and you need to change behavior at runtime based on state transitions.',
        solution: 'Define state classes for each state. The context delegates state-specific behavior to the current state object.',
        useCases: [
            'Order processing workflows',
            'Document editing states',
            'Game character states',
            'TCP connection states',
            'Vending machine operations'
        ],
        consequences: {
            positive: [
                'Localizes state-specific behavior (SRP)',
                'Makes transitions explicit',
                'State objects can be shared (Flyweight)'
            ],
            negative: [
                'Can result in many state classes',
                'State transitions can become complex'
            ]
        },
        relatedPatterns: ['Flyweight', 'Singleton', 'Strategy'],
        codeExample: `public interface IOrderState
{
    void Handle(Order order);
    void Ship(Order order);
    void Cancel(Order order);
}

public class PendingState : IOrderState
{
    public void Handle(Order order)
    {
        Console.WriteLine("Processing order...");
        order.State = new ProcessedState();
    }
    public void Ship(Order order) 
        => Console.WriteLine("Cannot ship pending order");
    public void Cancel(Order order)
    {
        Console.WriteLine("Order cancelled");
        order.State = new CancelledState();
    }
}

public class Order
{
    public IOrderState State { get; set; } = new PendingState();
    
    public void Handle() => State.Handle(this);
    public void Ship() => State.Ship(this);
    public void Cancel() => State.Cancel(this);
}`,
        cortexUsage: 'CORTEX uses State for orchestrator workflow states (planning, executing, completed) and conversation context states. Use for objects with complex state-dependent behavior.'
    },

    'strategy': {
        name: 'Strategy',
        type: 'behavioral',
        intent: 'Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it.',
        problem: 'You need to use different variants of an algorithm within an object and switch between them at runtime.',
        solution: 'Define a strategy interface for the algorithm. Create concrete strategy classes for each variant. Context uses strategy through the interface.',
        useCases: [
            'Sorting algorithms',
            'Payment processing methods',
            'Route calculation algorithms',
            'Compression algorithms',
            'Authentication strategies'
        ],
        consequences: {
            positive: [
                'Algorithms can vary independently (OCP)',
                'Isolates algorithm code (SRP)',
                'Runtime algorithm switching',
                'Eliminates conditional statements'
            ],
            negative: [
                'Clients must know strategies to select',
                'Increased number of objects'
            ]
        },
        relatedPatterns: ['Bridge', 'State', 'Template Method'],
        codeExample: `public interface IRouteStrategy
{
    void BuildRoute(string start, string end);
}

public class CarRouteStrategy : IRouteStrategy
{
    public void BuildRoute(string start, string end)
        => Console.WriteLine($"Driving from {start} to {end}");
}

public class WalkingRouteStrategy : IRouteStrategy
{
    public void BuildRoute(string start, string end)
        => Console.WriteLine($"Walking from {start} to {end}");
}

public class Navigator
{
    private IRouteStrategy _strategy;
    
    public void SetStrategy(IRouteStrategy strategy) 
        => _strategy = strategy;
    
    public void BuildRoute(string start, string end)
        => _strategy.BuildRoute(start, end);
}

// Usage
var nav = new Navigator();
nav.SetStrategy(new CarRouteStrategy());
nav.BuildRoute("A", "B"); // Driving from A to B`,
        cortexUsage: 'CORTEX uses Strategy for interchangeable response formatters and search algorithms. The response-templates system uses Strategy for format selection.'
    },

    'template-method': {
        name: 'Template Method',
        type: 'behavioral',
        intent: 'Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps without changing the algorithm\'s structure.',
        problem: 'You have several classes with similar algorithms but different implementations of some steps.',
        solution: 'Define the algorithm skeleton in a base class template method. Subclasses override abstract or virtual methods to customize specific steps.',
        useCases: [
            'Framework hooks (ASP.NET lifecycle)',
            'Data processing pipelines',
            'Document generation',
            'Test frameworks (setup/teardown)',
            'Game turn sequences'
        ],
        consequences: {
            positive: [
                'Code reuse through inheritance',
                'Inverted control (framework calls your code)',
                'Common behavior in one place'
            ],
            negative: [
                'Limited flexibility (subclassing required)',
                'Can be hard to maintain large template methods'
            ]
        },
        relatedPatterns: ['Factory Method', 'Strategy'],
        codeExample: `public abstract class DataExporter
{
    // Template method - defines algorithm skeleton
    public void Export(string data)
    {
        var processed = PreProcess(data);
        var formatted = Format(processed);
        Save(formatted);
        PostProcess();
    }
    
    protected virtual string PreProcess(string data) => data;
    protected abstract string Format(string data); // Must override
    protected abstract void Save(string data);     // Must override
    protected virtual void PostProcess() { }       // Optional hook
}

public class JsonExporter : DataExporter
{
    protected override string Format(string data)
        => JsonSerializer.Serialize(data);
    
    protected override void Save(string data)
        => File.WriteAllText("output.json", data);
}`,
        cortexUsage: 'CORTEX uses Template Method for orchestrator execution workflows and response rendering pipelines. The base orchestrator class defines the algorithm structure.'
    },

    'visitor': {
        name: 'Visitor',
        type: 'behavioral',
        intent: 'Represent an operation to be performed on elements of an object structure. Visitor lets you define a new operation without changing the classes of the elements on which it operates.',
        problem: 'You need to perform operations on all elements of a complex structure without modifying the element classes.',
        solution: 'Define a visitor interface with visit methods for each element type. Elements have an Accept method that calls the appropriate visit method.',
        useCases: [
            'Compilers (syntax tree operations)',
            'Document structure operations',
            'Shopping cart calculations',
            'Report generation',
            'Object serialization'
        ],
        consequences: {
            positive: [
                'Easy to add new operations (OCP)',
                'Related operations grouped in visitor (SRP)',
                'Can accumulate state while visiting'
            ],
            negative: [
                'Adding new element types is hard',
                'Might break encapsulation'
            ]
        },
        relatedPatterns: ['Composite', 'Interpreter', 'Iterator'],
        codeExample: `public interface IVisitor
{
    void Visit(Book book);
    void Visit(Electronics electronics);
}

public abstract class Product
{
    public decimal Price { get; set; }
    public abstract void Accept(IVisitor visitor);
}

public class Book : Product
{
    public override void Accept(IVisitor visitor) => visitor.Visit(this);
}

public class TaxVisitor : IVisitor
{
    public decimal TotalTax { get; private set; }
    
    public void Visit(Book book) 
        => TotalTax += book.Price * 0.05m; // 5% tax
    
    public void Visit(Electronics electronics)
        => TotalTax += electronics.Price * 0.15m; // 15% tax
}

// Usage
var visitor = new TaxVisitor();
foreach (var product in cart)
    product.Accept(visitor);
Console.WriteLine($"Total tax: {visitor.TotalTax}");`,
        cortexUsage: 'CORTEX uses Visitor for traversing knowledge graphs and applying operations across document structures. Useful for operations that span multiple object types.'
    },

    // ============================================
    // ENTERPRISE PATTERNS (2)
    // ============================================
    'repository': {
        name: 'Repository',
        type: 'enterprise',
        intent: 'Mediate between the domain and data mapping layers using a collection-like interface for accessing domain objects.',
        problem: 'You want to decouple business logic from data access logic and provide a consistent interface for data operations.',
        solution: 'Define a repository interface that provides methods for retrieving and persisting domain objects. Implementation handles the actual data access.',
        useCases: [
            'Abstracting database access',
            'Unit testing with mock repositories',
            'Switching data sources',
            'Centralizing data access logic',
            'Implementing caching layers'
        ],
        consequences: {
            positive: [
                'Decouples business logic from data access',
                'Enables unit testing with mocks',
                'Centralizes data access logic',
                'Easy to switch implementations'
            ],
            negative: [
                'Additional abstraction layer',
                'Can hide ORM features unnecessarily',
                'Often overused for simple scenarios'
            ]
        },
        relatedPatterns: ['Unit of Work', 'Factory Method'],
        codeExample: `public interface IRepository<T> where T : class
{
    T GetById(int id);
    IEnumerable<T> GetAll();
    IEnumerable<T> Find(Expression<Func<T, bool>> predicate);
    void Add(T entity);
    void Update(T entity);
    void Delete(T entity);
}

public class CustomerRepository : IRepository<Customer>
{
    private readonly DbContext _context;
    
    public CustomerRepository(DbContext context) => _context = context;
    
    public Customer GetById(int id) 
        => _context.Set<Customer>().Find(id);
    
    public IEnumerable<Customer> GetAll() 
        => _context.Set<Customer>().ToList();
    
    public void Add(Customer entity) 
        => _context.Set<Customer>().Add(entity);
    
    // ... other methods
}`,
        cortexUsage: 'CORTEX uses Repository for brain data access operations. Each brain tier has its repository for accessing and persisting knowledge. Use for consistent data access abstraction.'
    },

    'unit-of-work': {
        name: 'Unit of Work',
        type: 'enterprise',
        intent: 'Maintain a list of objects affected by a business transaction and coordinate the writing out of changes and the resolution of concurrency problems.',
        problem: 'You need to track changes to multiple objects and persist them atomically as a single transaction.',
        solution: 'Create a UnitOfWork class that tracks changes and coordinates commits. Often wraps multiple repositories and shares the same database context.',
        useCases: [
            'Transactional database operations',
            'Coordinating multiple repository operations',
            'Tracking entity changes',
            'Batch updates',
            'Atomic operations across aggregates'
        ],
        consequences: {
            positive: [
                'Ensures data consistency',
                'Batches database operations (performance)',
                'Tracks changed entities automatically',
                'Simplifies transaction management'
            ],
            negative: [
                'Additional complexity',
                'Memory overhead from tracking changes',
                'Can mask individual operation issues'
            ]
        },
        relatedPatterns: ['Repository', 'Identity Map'],
        codeExample: `public interface IUnitOfWork : IDisposable
{
    IRepository<Customer> Customers { get; }
    IRepository<Order> Orders { get; }
    int Complete(); // Save changes
}

public class UnitOfWork : IUnitOfWork
{
    private readonly DbContext _context;
    
    public UnitOfWork(DbContext context)
    {
        _context = context;
        Customers = new CustomerRepository(_context);
        Orders = new OrderRepository(_context);
    }
    
    public IRepository<Customer> Customers { get; }
    public IRepository<Order> Orders { get; }
    
    public int Complete() => _context.SaveChanges();
    
    public void Dispose() => _context.Dispose();
}

// Usage - atomic operation across repositories
using (var uow = new UnitOfWork(new AppDbContext()))
{
    uow.Customers.Add(customer);
    uow.Orders.Add(order);
    uow.Complete(); // Single transaction
}`,
        cortexUsage: 'CORTEX uses Unit of Work for atomic brain state updates. When updating multiple brain tiers, changes are coordinated through a UnitOfWork. Note: EF Core\'s DbContext implements this pattern.'
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PATTERNS_DATA;
}
