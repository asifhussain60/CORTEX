/**
 * Mock Database
 * In-memory database with localStorage persistence
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { AppConfig } from '../config.js';
import { Logger } from '../utils/logger.js';
import { StorageManager } from '../utils/storage.js';
import { Task, User, Comment } from '../domain/entities.js';
import { Priority, Status, Role } from '../domain/enums.js';

/**
 * MockDatabase class
 * Manages in-memory collections with localStorage persistence
 */
export class MockDatabase {
    constructor() {
        this.tasks = [];
        this.users = [];
        this.roles = Object.values(Role);
        
        Logger.info('MockDatabase initialized');
        this.loadFromStorage();
    }

    /**
     * Load data from localStorage
     */
    loadFromStorage() {
        try {
            const storedTasks = StorageManager.get(AppConfig.storage.tasksKey, []);
            const storedUsers = StorageManager.get(AppConfig.storage.usersKey, []);
            
            this.tasks = storedTasks.map(t => Task.fromJSON(t));
            this.users = storedUsers.map(u => User.fromJSON(u));
            
            Logger.info(`Loaded ${this.tasks.length} tasks and ${this.users.length} users from storage`);
        } catch (error) {
            Logger.error('Failed to load from storage', error);
            this.tasks = [];
            this.users = [];
        }
    }

    /**
     * Save data to localStorage
     */
    saveToStorage() {
        try {
            const tasksJson = this.tasks.map(t => t.toJSON());
            const usersJson = this.users.map(u => u.toStorageJSON());
            
            StorageManager.set(AppConfig.storage.tasksKey, tasksJson);
            StorageManager.set(AppConfig.storage.usersKey, usersJson);
            
            Logger.debug('Database saved to storage');
        } catch (error) {
            Logger.error('Failed to save to storage', error);
        }
    }

    /**
     * Check if database has been seeded
     * @returns {boolean} True if seeded
     */
    isSeeded() {
        return StorageManager.get(AppConfig.storage.dbSeededKey, false);
    }

    /**
     * Mark database as seeded
     */
    markSeeded() {
        StorageManager.set(AppConfig.storage.dbSeededKey, true);
    }

    /**
     * Seed database with sample data
     */
    seed() {
        if (this.isSeeded()) {
            Logger.info('Database already seeded, skipping...');
            return;
        }

        Logger.info('Seeding database with sample data...');

        // Create users (passwords will be hashed by security module)
        const adminUser = new User(
            'admin',
            'admin@cortex-sdd.com',
            'Admin@123', // Will be hashed
            Role.Admin,
            'user-admin',
            'System Administrator',
            new Date('2025-01-01')
        );

        const teamLeadUser = new User(
            'teamlead',
            'teamlead@cortex-sdd.com',
            'TeamLead@123', // Will be hashed
            Role.TeamLead,
            'user-teamlead',
            'Team Lead User',
            new Date('2025-01-05')
        );

        const regularUser = new User(
            'user',
            'user@cortex-sdd.com',
            'User@123', // Will be hashed
            Role.User,
            'user-regular',
            'Regular User',
            new Date('2025-01-10')
        );

        this.users.push(adminUser, teamLeadUser, regularUser);

        // Create sample tasks
        const task1 = new Task(
            'Implement user authentication',
            'Create login and registration functionality with JWT tokens',
            Priority.Critical,
            Status.Completed,
            'task-1',
            'user-admin',
            'user-admin',
            new Date('2025-01-15'),
            new Date('2025-01-20'),
            ['authentication', 'security']
        );
        task1.addComment(new Comment('Started implementation', 'user-admin', 'comment-1', new Date('2025-01-15')));
        task1.addComment(new Comment('Completed and tested', 'user-admin', 'comment-2', new Date('2025-01-20')));

        const task2 = new Task(
            'Design task management UI',
            'Create responsive UI components for task list, filters, and forms',
            Priority.High,
            Status.InProgress,
            'task-2',
            'user-teamlead',
            'user-admin',
            new Date('2025-01-18'),
            new Date('2025-02-01'),
            ['ui', 'design']
        );
        task2.addComment(new Comment('Wireframes approved', 'user-teamlead', 'comment-3', new Date('2025-01-18')));

        const task3 = new Task(
            'Setup mock database layer',
            'Implement in-memory database with localStorage persistence',
            Priority.High,
            Status.Completed,
            'task-3',
            'user-admin',
            'user-teamlead',
            new Date('2025-01-12'),
            new Date('2025-01-17'),
            ['database', 'infrastructure']
        );

        const task4 = new Task(
            'Implement task filtering',
            'Add filters for status, priority, assignee, and date range',
            Priority.Medium,
            Status.Open,
            'task-4',
            'user-regular',
            'user-teamlead',
            new Date('2025-01-20'),
            new Date('2025-02-05'),
            ['features']
        );

        const task5 = new Task(
            'Write unit tests',
            'Create comprehensive test suite covering all layers',
            Priority.High,
            Status.Testing,
            'task-5',
            'user-teamlead',
            'user-admin',
            new Date('2025-01-22'),
            new Date('2025-02-01'),
            ['testing', 'quality']
        );

        const task6 = new Task(
            'Performance optimization',
            'Optimize rendering and state management',
            Priority.Low,
            Status.Open,
            'task-6',
            null,
            'user-admin',
            new Date('2025-01-25'),
            new Date('2025-02-15'),
            ['performance']
        );

        const task7 = new Task(
            'Security audit',
            'Review authentication, authorization, and data validation',
            Priority.Critical,
            Status.Blocked,
            'task-7',
            'user-admin',
            'user-admin',
            new Date('2025-01-28'),
            new Date('2025-02-10'),
            ['security', 'audit']
        );
        task7.addComment(new Comment('Waiting for third-party security review', 'user-admin', 'comment-4', new Date('2025-01-28')));

        this.tasks.push(task1, task2, task3, task4, task5, task6, task7);

        this.saveToStorage();
        this.markSeeded();

        Logger.info(`Database seeded with ${this.users.length} users and ${this.tasks.length} tasks`);
    }

    /**
     * Clear all data
     */
    clear() {
        this.tasks = [];
        this.users = [];
        StorageManager.remove(AppConfig.storage.tasksKey);
        StorageManager.remove(AppConfig.storage.usersKey);
        StorageManager.remove(AppConfig.storage.dbSeededKey);
        Logger.info('Database cleared');
    }

    /**
     * Reset database (clear and reseed)
     */
    reset() {
        this.clear();
        this.seed();
        Logger.info('Database reset complete');
    }

    /**
     * Get database statistics
     * @returns {Object} Statistics object
     */
    getStats() {
        return {
            totalTasks: this.tasks.length,
            totalUsers: this.users.length,
            completedTasks: this.tasks.filter(t => t.status === Status.Completed).length,
            openTasks: this.tasks.filter(t => t.status === Status.Open).length,
            inProgressTasks: this.tasks.filter(t => t.status === Status.InProgress).length,
            blockedTasks: this.tasks.filter(t => t.status === Status.Blocked).length,
            overdueTasks: this.tasks.filter(t => t.isOverdue()).length,
            storageUsed: StorageManager.getSizeFormatted()
        };
    }
}

// Singleton instance
let dbInstance = null;

/**
 * Get database instance (singleton)
 * @returns {MockDatabase} Database instance
 */
export function getDatabase() {
    if (!dbInstance) {
        dbInstance = new MockDatabase();
        // Auto-seed if empty
        if (dbInstance.tasks.length === 0 && dbInstance.users.length === 0) {
            dbInstance.seed();
        }
    }
    return dbInstance;
}

export default { MockDatabase, getDatabase };
