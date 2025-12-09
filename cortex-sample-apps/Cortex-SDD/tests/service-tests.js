/**
 * Service Layer Tests
 * Tests for application services, validators, and DTOs
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Assert, TestRunner } from './unit-tests.js';
import { TaskService, AuthService, UserService } from '../js/application/services.js';
import { TaskValidator, LoginValidator, RegisterValidator } from '../js/application/validators.js';
import { TaskDto, LoginDto, RegisterDto } from '../js/application/dtos.js';
import { MockDatabase } from '../js/infrastructure/mock-db.js';

/**
 * Service Layer Test Suite
 */
export class ServiceTests {
    static async runAll() {
        const runner = new TestRunner('Service Layer Tests');

        // DTO Tests
        runner.addTest('TaskDto.create() should create empty DTO', () => {
            const dto = TaskDto.create();
            Assert.areEqual(dto.id, null);
            Assert.areEqual(dto.title, '');
            Assert.isFalse(dto.isCompleted);
        });

        runner.addTest('TaskDto.fromEntity() should map entity correctly', () => {
            const task = {
                id: 1,
                title: 'Test Task',
                isCompleted: false,
                userId: 1,
                createdAt: new Date(),
                updatedAt: new Date()
            };
            const dto = TaskDto.fromEntity(task);
            Assert.areEqual(dto.id, 1);
            Assert.areEqual(dto.title, 'Test Task');
            Assert.isFalse(dto.isCompleted);
        });

        // Validator Tests
        runner.addTest('TaskValidator should reject empty title', () => {
            const dto = TaskDto.create({ title: '' });
            const result = TaskValidator.validate(dto);
            Assert.isFalse(result.isValid);
            Assert.isTrue(result.hasError('title'));
        });

        runner.addTest('TaskValidator should reject title >255 chars', () => {
            const dto = TaskDto.create({ title: 'A'.repeat(256) });
            const result = TaskValidator.validate(dto);
            Assert.isFalse(result.isValid);
            Assert.isTrue(result.hasError('title'));
        });

        runner.addTest('TaskValidator should accept valid task', () => {
            const dto = TaskDto.create({ title: 'Valid Task', userId: 1 });
            const result = TaskValidator.validate(dto);
            Assert.isTrue(result.isValid);
            Assert.areEqual(result.errors.length, 0);
        });

        runner.addTest('LoginValidator should reject empty credentials', () => {
            const dto = LoginDto.create('', '');
            const result = LoginValidator.validate(dto);
            Assert.isFalse(result.isValid);
            Assert.isTrue(result.hasError('usernameOrEmail'));
            Assert.isTrue(result.hasError('password'));
        });

        runner.addTest('RegisterValidator should reject weak password', () => {
            const dto = RegisterDto.create({
                username: 'testuser',
                email: 'test@example.com',
                password: 'weak',
                confirmPassword: 'weak'
            });
            const result = RegisterValidator.validate(dto);
            Assert.isFalse(result.isValid);
            Assert.isTrue(result.hasError('password'));
        });

        runner.addTest('RegisterValidator should reject password mismatch', () => {
            const dto = RegisterDto.create({
                username: 'testuser',
                email: 'test@example.com',
                password: 'Strong123',
                confirmPassword: 'Different456'
            });
            const result = RegisterValidator.validate(dto);
            Assert.isFalse(result.isValid);
            Assert.isTrue(result.hasError('confirmPassword'));
        });

        runner.addTest('RegisterValidator should accept valid registration', () => {
            const dto = RegisterDto.create({
                username: 'testuser',
                email: 'test@example.com',
                password: 'Strong123',
                confirmPassword: 'Strong123'
            });
            const result = RegisterValidator.validate(dto);
            Assert.isTrue(result.isValid);
        });

        // TaskService Tests
        runner.addTest('TaskService.createTask() should create task for user', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new TaskService();
            const dto = TaskDto.create({ title: 'New Task' });
            const result = await service.createTask(dto, 2); // User ID 2
            
            Assert.isNotNull(result.id);
            Assert.areEqual(result.title, 'New Task');
            Assert.areEqual(result.userId, 2);
        });

        runner.addTest('TaskService.createTask() should reject invalid task', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new TaskService();
            const dto = TaskDto.create({ title: '' }); // Empty title
            
            try {
                await service.createTask(dto, 2);
                Assert.fail('Should have thrown validation error');
            } catch (error) {
                Assert.isTrue(error.message.includes('Validation failed'));
            }
        });

        runner.addTest('TaskService.getAllTasks() should return only user tasks', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new TaskService();
            const tasks = await service.getAllTasks(2); // Regular user
            
            // Regular user should only see their own tasks
            Assert.isTrue(tasks.every(t => t.userId === 2));
        });

        runner.addTest('TaskService.getAllTasks() should return all tasks for admin', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new TaskService();
            const tasks = await service.getAllTasks(1); // Admin user
            
            // Admin should see all tasks
            Assert.isTrue(tasks.length > 0);
        });

        runner.addTest('TaskService.updateTask() should reject unauthorized update', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new TaskService();
            
            // User 2 tries to update User 3's task
            const dto = TaskDto.create({ title: 'Hacked Task' });
            
            try {
                await service.updateTask(3, dto, 2); // Task 3 belongs to User 3
                Assert.fail('Should have thrown unauthorized error');
            } catch (error) {
                Assert.isTrue(error.message.includes('Unauthorized'));
            }
        });

        runner.addTest('TaskService.deleteTask() should allow user to delete own task', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new TaskService();
            const result = await service.deleteTask(2, 2); // User 2 deletes own task
            
            Assert.isTrue(result);
        });

        runner.addTest('TaskService.toggleTaskCompletion() should toggle status', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new TaskService();
            const task = await service.getTaskById(2, 2);
            const originalStatus = task.isCompleted;
            
            const updated = await service.toggleTaskCompletion(2, 2);
            Assert.areEqual(updated.isCompleted, !originalStatus);
        });

        // AuthService Tests
        runner.addTest('AuthService.login() should authenticate valid user', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new AuthService();
            const dto = LoginDto.create('admin', 'Admin@123');
            const result = await service.login(dto);
            
            Assert.isNotNull(result.token);
            Assert.areEqual(result.user.username, 'admin');
        });

        runner.addTest('AuthService.login() should reject invalid password', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new AuthService();
            const dto = LoginDto.create('admin', 'WrongPassword');
            
            try {
                await service.login(dto);
                Assert.fail('Should have thrown invalid credentials error');
            } catch (error) {
                Assert.areEqual(error.message, 'Invalid credentials');
            }
        });

        runner.addTest('AuthService.login() should reject non-existent user', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new AuthService();
            const dto = LoginDto.create('nonexistent', 'password');
            
            try {
                await service.login(dto);
                Assert.fail('Should have thrown invalid credentials error');
            } catch (error) {
                Assert.areEqual(error.message, 'Invalid credentials');
            }
        });

        runner.addTest('AuthService.register() should create new user', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new AuthService();
            const dto = RegisterDto.create({
                username: 'newuser',
                email: 'newuser@example.com',
                password: 'NewUser123',
                confirmPassword: 'NewUser123'
            });
            
            const result = await service.register(dto);
            
            Assert.isNotNull(result.token);
            Assert.areEqual(result.user.username, 'newuser');
            Assert.areEqual(result.user.email, 'newuser@example.com');
        });

        runner.addTest('AuthService.register() should reject duplicate username', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new AuthService();
            const dto = RegisterDto.create({
                username: 'admin', // Already exists
                email: 'newemail@example.com',
                password: 'NewUser123',
                confirmPassword: 'NewUser123'
            });
            
            try {
                await service.register(dto);
                Assert.fail('Should have thrown username exists error');
            } catch (error) {
                Assert.isTrue(error.message.includes('Username already exists'));
            }
        });

        runner.addTest('AuthService.register() should reject duplicate email', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new AuthService();
            const dto = RegisterDto.create({
                username: 'newuser',
                email: 'admin@cortex-sdd.com', // Already exists
                password: 'NewUser123',
                confirmPassword: 'NewUser123'
            });
            
            try {
                await service.register(dto);
                Assert.fail('Should have thrown email exists error');
            } catch (error) {
                Assert.isTrue(error.message.includes('Email already exists'));
            }
        });

        runner.addTest('AuthService.validateToken() should validate valid token', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new AuthService();
            const loginDto = LoginDto.create('admin', 'Admin@123');
            const authResult = await service.login(loginDto);
            
            const payload = service.validateToken(authResult.token);
            Assert.isNotNull(payload);
            Assert.areEqual(payload.username, 'admin');
        });

        runner.addTest('AuthService.getCurrentUser() should return user from token', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new AuthService();
            const loginDto = LoginDto.create('admin', 'Admin@123');
            const authResult = await service.login(loginDto);
            
            const user = await service.getCurrentUser(authResult.token);
            Assert.areEqual(user.username, 'admin');
            Assert.areEqual(user.email, 'admin@cortex-sdd.com');
        });

        // UserService Tests
        runner.addTest('UserService.getUserById() should return user', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new UserService();
            const user = await service.getUserById(1);
            
            Assert.areEqual(user.username, 'admin');
            Assert.areEqual(user.roleName, 'Administrator');
        });

        runner.addTest('UserService.getAllUsers() should reject non-admin', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new UserService();
            
            try {
                await service.getAllUsers(2); // Regular user
                Assert.fail('Should have thrown unauthorized error');
            } catch (error) {
                Assert.isTrue(error.message.includes('Unauthorized'));
            }
        });

        runner.addTest('UserService.getAllUsers() should return all users for admin', async () => {
            MockDatabase.clear();
            await MockDatabase.seed();
            
            const service = new UserService();
            const users = await service.getAllUsers(1); // Admin user
            
            Assert.isTrue(users.length >= 3); // At least admin, teamlead, user
        });

        // Run all tests
        await runner.run();
        return runner.getResults();
    }
}

// Auto-run tests when module is loaded
if (typeof window !== 'undefined') {
    window.ServiceTests = ServiceTests;
}
