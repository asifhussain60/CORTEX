/**
 * Cortex-SDD Test Framework
 * Custom vanilla JavaScript testing framework
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

/**
 * Test assertion utilities
 */
export class Assert {
    static isTrue(condition, message = 'Expected true') {
        if (!condition) {
            throw new Error(message);
        }
    }

    static isFalse(condition, message = 'Expected false') {
        if (condition) {
            throw new Error(message);
        }
    }

    static areEqual(actual, expected, message = 'Values not equal') {
        if (actual !== expected) {
            throw new Error(`${message}. Expected: ${expected}, Actual: ${actual}`);
        }
    }

    static areNotEqual(actual, expected, message = 'Values should not be equal') {
        if (actual === expected) {
            throw new Error(`${message}. Both values: ${actual}`);
        }
    }

    static isNull(value, message = 'Expected null') {
        if (value !== null) {
            throw new Error(`${message}. Actual: ${value}`);
        }
    }

    static isNotNull(value, message = 'Expected not null') {
        if (value === null) {
            throw new Error(message);
        }
    }

    static isUndefined(value, message = 'Expected undefined') {
        if (value !== undefined) {
            throw new Error(`${message}. Actual: ${value}`);
        }
    }

    static isDefined(value, message = 'Expected defined value') {
        if (value === undefined) {
            throw new Error(message);
        }
    }

    static throws(fn, message = 'Expected function to throw') {
        try {
            fn();
            throw new Error(message);
        } catch (error) {
            if (error.message === message) {
                throw error;
            }
        }
    }

    static doesNotThrow(fn, message = 'Expected function not to throw') {
        try {
            fn();
        } catch (error) {
            throw new Error(`${message}. Error: ${error.message}`);
        }
    }

    static arrayContains(array, item, message = 'Array does not contain item') {
        if (!array.includes(item)) {
            throw new Error(`${message}. Item: ${item}`);
        }
    }

    static deepEqual(actual, expected, message = 'Objects not deeply equal') {
        const actualJson = JSON.stringify(actual);
        const expectedJson = JSON.stringify(expected);
        if (actualJson !== expectedJson) {
            throw new Error(`${message}. Expected: ${expectedJson}, Actual: ${actualJson}`);
        }
    }
}

/**
 * Test suite class
 */
class TestSuite {
    constructor(name) {
        this.name = name;
        this.tests = [];
    }

    addTest(name, fn) {
        this.tests.push({ name, fn, status: 'pending', error: null });
    }

    async run() {
        for (const test of this.tests) {
            try {
                await test.fn();
                test.status = 'passed';
            } catch (error) {
                test.status = 'failed';
                test.error = error.message;
            }
        }
    }
}

/**
 * Test runner class
 */
export class TestRunner {
    constructor() {
        this.suites = [];
    }

    describe(suiteName, fn) {
        const suite = new TestSuite(suiteName);
        this.suites.push(suite);
        
        const it = (testName, testFn) => {
            suite.addTest(testName, testFn);
        };
        
        fn(it);
    }

    async run() {
        for (const suite of this.suites) {
            await suite.run();
        }
    }

    getResults() {
        const results = {
            passed: 0,
            failed: 0,
            pending: 0,
            suites: []
        };

        this.suites.forEach(suite => {
            const suiteResult = {
                name: suite.name,
                tests: []
            };

            suite.tests.forEach(test => {
                suiteResult.tests.push({
                    name: test.name,
                    status: test.status,
                    error: test.error
                });

                if (test.status === 'passed') results.passed++;
                else if (test.status === 'failed') results.failed++;
                else results.pending++;
            });

            results.suites.push(suiteResult);
        });

        return results;
    }
}

// ============================================================
// TDD GREEN PHASE: Import implemented modules
// ============================================================

import { Task, User, Comment } from '../js/domain/entities.js';
import { Priority, Status, Role } from '../js/domain/enums.js';
import { MockDatabase } from '../js/infrastructure/mock-db.js';
import { TaskRepository, UserRepository } from '../js/infrastructure/repositories.js';

// ============================================================
// Unit Tests
// ============================================================

const runner = new TestRunner();

// Domain Layer Tests
runner.describe('Task Entity', (it) => {
    it('should create task with valid data', () => {
        const task = new Task('Test Task', 'Description', Priority.Medium, Status.Open);
        Assert.isNotNull(task);
        Assert.areEqual(task.title, 'Test Task');
    });

    it('should validate required fields', () => {
        Assert.throws(() => {
            new Task('', 'Description', Priority.Medium, Status.Open);
        });
    });

    it('should generate unique ID', () => {
        const task1 = new Task('Task 1', 'Desc', Priority.Low, Status.Open);
        const task2 = new Task('Task 2', 'Desc', Priority.Low, Status.Open);
        Assert.areNotEqual(task1.id, task2.id);
    });
});

runner.describe('User Entity', (it) => {
    it('should create user with valid data', () => {
        const user = new User('testuser', 'test@example.com', 'hashedPassword', Role.User);
        Assert.areEqual(user.username, 'testuser');
        Assert.areEqual(user.email, 'test@example.com');
    });

    it('should validate email format', () => {
        Assert.throws(() => {
            new User('testuser', 'invalid-email', 'hashedPassword', Role.User);
        });
    });
});

// Infrastructure Layer Tests
runner.describe('MockDatabase', (it) => {
    it('should initialize with collections', () => {
        const db = new MockDatabase();
        Assert.isTrue(Array.isArray(db.tasks));
        Assert.isTrue(Array.isArray(db.users));
    });

    it('should have seeded data', () => {
        const db = new MockDatabase();
        // Database auto-seeds on first initialization
        Assert.isTrue(db.tasks.length > 0);
        Assert.isTrue(db.users.length > 0);
    });
});

runner.describe('TaskRepository', (it) => {
    it('should get all tasks', async () => {
        const repo = new TaskRepository();
        const tasks = await repo.getAll();
        Assert.isTrue(Array.isArray(tasks));
    });

    it('should create new task', async () => {
        const repo = new TaskRepository();
        const taskDto = { title: 'New Task', description: 'Desc', priority: 2, status: 1 };
        const created = await repo.create(taskDto);
        Assert.isNotNull(created.id);
    });

    it('should update existing task', async () => {
        const repo = new TaskRepository();
        const tasks = await repo.getAll();
        if (tasks.length > 0) {
            const updated = await repo.update(tasks[0].id, { title: 'Updated Title' });
            Assert.areEqual(updated.title, 'Updated Title');
        }
    });

    it('should delete task', async () => {
        const repo = new TaskRepository();
        const taskDto = { title: 'Task to Delete', description: 'Desc', priority: 1, status: 1 };
        const created = await repo.create(taskDto);
        const result = await repo.delete(created.id);
        Assert.isTrue(result);
    });
});

// Application Layer Tests (RED - Not implemented yet)
runner.describe('TaskService', (it) => {
    it('should get tasks with filters - PENDING', async () => {
        // Will implement in Phase 2
    });

    it('should validate task before creation - PENDING', async () => {
        // Will implement in Phase 2
    });
});

runner.describe('AuthService', (it) => {
    it('should authenticate valid credentials - PENDING', async () => {
        // Will implement in Phase 2
    });

    it('should reject invalid credentials - PENDING', async () => {
        // Will implement in Phase 2
    });

    it('should generate JWT token - PENDING', async () => {
        // Will implement in Phase 2
    });
});

// Presentation Layer Tests (RED - Not implemented yet)
runner.describe('Router', (it) => {
    it('should register routes - PENDING', () => {
        // Will implement in Phase 3
    });

    it('should navigate to route - PENDING', () => {
        // Will implement in Phase 3
    });
});

export default runner;
