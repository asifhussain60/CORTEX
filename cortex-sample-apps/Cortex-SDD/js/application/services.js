/**
 * Application Services Layer
 * Business logic and authorization
 * 
 * @module application/services
 * @author Asif Hussain
 * @version 1.0.0
 */

import { TaskRepository, UserRepository, RoleRepository } from '../infrastructure/repositories.js';
import { JwtSimulator, PasswordHasher } from '../infrastructure/security.js';
import { TaskDto, UserDto, AuthResponseDto } from './dtos.js';
import { TaskValidator, LoginValidator, RegisterValidator } from './validators.js';
import { UserRole } from '../domain/enums.js';

/**
 * Task Service
 * Handles task business logic and authorization
 */
export class TaskService {
    constructor() {
        this.taskRepository = new TaskRepository();
        this.userRepository = new UserRepository();
    }

    /**
     * Get all tasks for a user
     * @param {number} userId - User ID
     * @param {Object} filters - Optional filters
     * @returns {Array<Object>} Task DTOs
     */
    async getAllTasks(userId, filters = {}) {
        const user = await this.userRepository.getById(userId);
        if (!user) {
            throw new Error('User not found');
        }

        let tasks;
        
        // Admin can see all tasks
        if (user.roleId === UserRole.ADMIN) {
            tasks = await this.taskRepository.getAll();
        } else {
            // Regular users see only their tasks
            tasks = await this.taskRepository.getByUserId(userId);
        }

        // Apply filters
        if (filters.isCompleted !== undefined && filters.isCompleted !== null) {
            tasks = tasks.filter(t => t.isCompleted === filters.isCompleted);
        }

        if (filters.searchTerm) {
            const searchLower = filters.searchTerm.toLowerCase();
            tasks = tasks.filter(t => t.title.toLowerCase().includes(searchLower));
        }

        // Map to DTOs
        return tasks.map(task => TaskDto.fromEntity(task));
    }

    /**
     * Get task by ID
     * @param {number} taskId - Task ID
     * @param {number} userId - Current user ID
     * @returns {Object} Task DTO
     */
    async getTaskById(taskId, userId) {
        const task = await this.taskRepository.getById(taskId);
        if (!task) {
            throw new Error('Task not found');
        }

        // Authorization check
        const user = await this.userRepository.getById(userId);
        if (user.roleId !== UserRole.ADMIN && task.userId !== userId) {
            throw new Error('Unauthorized: You can only access your own tasks');
        }

        return TaskDto.fromEntity(task);
    }

    /**
     * Create a new task
     * @param {Object} taskDto - Task DTO
     * @param {number} userId - Current user ID
     * @returns {Object} Created task DTO
     */
    async createTask(taskDto, userId) {
        // Validation
        const validation = TaskValidator.validate(taskDto);
        if (!validation.isValid) {
            throw new Error(`Validation failed: ${validation.errors.map(e => e.message).join(', ')}`);
        }

        // Set user ID
        const taskData = TaskDto.toEntity(taskDto);
        taskData.userId = userId;

        // Create task
        const task = await this.taskRepository.create(taskData);
        return TaskDto.fromEntity(task);
    }

    /**
     * Update an existing task
     * @param {number} taskId - Task ID
     * @param {Object} taskDto - Updated task DTO
     * @param {number} userId - Current user ID
     * @returns {Object} Updated task DTO
     */
    async updateTask(taskId, taskDto, userId) {
        // Get existing task
        const existingTask = await this.taskRepository.getById(taskId);
        if (!existingTask) {
            throw new Error('Task not found');
        }

        // Authorization check
        const user = await this.userRepository.getById(userId);
        if (user.roleId !== UserRole.ADMIN && existingTask.userId !== userId) {
            throw new Error('Unauthorized: You can only modify your own tasks');
        }

        // Validation
        const validation = TaskValidator.validate(taskDto);
        if (!validation.isValid) {
            throw new Error(`Validation failed: ${validation.errors.map(e => e.message).join(', ')}`);
        }

        // Update task
        const updateData = {
            title: taskDto.title,
            isCompleted: taskDto.isCompleted
        };
        const updatedTask = await this.taskRepository.update(taskId, updateData);
        return TaskDto.fromEntity(updatedTask);
    }

    /**
     * Delete a task
     * @param {number} taskId - Task ID
     * @param {number} userId - Current user ID
     * @returns {boolean} Success
     */
    async deleteTask(taskId, userId) {
        // Get existing task
        const existingTask = await this.taskRepository.getById(taskId);
        if (!existingTask) {
            throw new Error('Task not found');
        }

        // Authorization check
        const user = await this.userRepository.getById(userId);
        if (user.roleId !== UserRole.ADMIN && existingTask.userId !== userId) {
            throw new Error('Unauthorized: You can only delete your own tasks');
        }

        return await this.taskRepository.delete(taskId);
    }

    /**
     * Toggle task completion status
     * @param {number} taskId - Task ID
     * @param {number} userId - Current user ID
     * @returns {Object} Updated task DTO
     */
    async toggleTaskCompletion(taskId, userId) {
        const task = await this.taskRepository.getById(taskId);
        if (!task) {
            throw new Error('Task not found');
        }

        // Authorization check
        const user = await this.userRepository.getById(userId);
        if (user.roleId !== UserRole.ADMIN && task.userId !== userId) {
            throw new Error('Unauthorized: You can only modify your own tasks');
        }

        const updatedTask = await this.taskRepository.update(taskId, {
            isCompleted: !task.isCompleted
        });
        return TaskDto.fromEntity(updatedTask);
    }
}

/**
 * Authentication Service
 * Handles user authentication and authorization
 */
export class AuthService {
    constructor() {
        this.userRepository = new UserRepository();
        this.roleRepository = new RoleRepository();
        this.jwtSimulator = new JwtSimulator();
        this.passwordHasher = new PasswordHasher();
    }

    /**
     * Login user
     * @param {Object} loginDto - Login credentials
     * @returns {Object} Auth response DTO
     */
    async login(loginDto) {
        // Validation
        const validation = LoginValidator.validate(loginDto);
        if (!validation.isValid) {
            throw new Error(`Validation failed: ${validation.errors.map(e => e.message).join(', ')}`);
        }

        // Find user by username or email
        let user = await this.userRepository.getByUsername(loginDto.usernameOrEmail);
        if (!user) {
            user = await this.userRepository.getByEmail(loginDto.usernameOrEmail);
        }

        if (!user) {
            throw new Error('Invalid credentials');
        }

        // Verify password
        const isValid = await this.passwordHasher.verify(loginDto.password, user.passwordHash);
        if (!isValid) {
            throw new Error('Invalid credentials');
        }

        // Get role
        const role = await this.roleRepository.getById(user.roleId);

        // Generate JWT token
        const token = this.jwtSimulator.generate({
            userId: user.id,
            username: user.username,
            email: user.email,
            roleId: user.roleId,
            roleName: role.name
        });

        // Create response
        const userDto = UserDto.fromEntity(user, role);
        return AuthResponseDto.create(userDto, token);
    }

    /**
     * Register new user
     * @param {Object} registerDto - Registration data
     * @returns {Object} Auth response DTO
     */
    async register(registerDto) {
        // Validation
        const validation = RegisterValidator.validate(registerDto);
        if (!validation.isValid) {
            throw new Error(`Validation failed: ${validation.errors.map(e => e.message).join(', ')}`);
        }

        // Check if username exists
        const existingUsername = await this.userRepository.getByUsername(registerDto.username);
        if (existingUsername) {
            throw new Error('Username already exists');
        }

        // Check if email exists
        const existingEmail = await this.userRepository.getByEmail(registerDto.email);
        if (existingEmail) {
            throw new Error('Email already exists');
        }

        // Hash password
        const passwordHash = await this.passwordHasher.hash(registerDto.password);

        // Create user with default User role
        const userData = {
            username: registerDto.username,
            email: registerDto.email,
            passwordHash: passwordHash,
            roleId: UserRole.USER
        };

        const user = await this.userRepository.create(userData);
        const role = await this.roleRepository.getById(user.roleId);

        // Generate JWT token
        const token = this.jwtSimulator.generate({
            userId: user.id,
            username: user.username,
            email: user.email,
            roleId: user.roleId,
            roleName: role.name
        });

        // Create response
        const userDto = UserDto.fromEntity(user, role);
        return AuthResponseDto.create(userDto, token);
    }

    /**
     * Validate JWT token
     * @param {string} token - JWT token
     * @returns {Object} Token payload
     */
    validateToken(token) {
        return this.jwtSimulator.validate(token);
    }

    /**
     * Get current user from token
     * @param {string} token - JWT token
     * @returns {Object} User DTO
     */
    async getCurrentUser(token) {
        const payload = this.validateToken(token);
        if (!payload) {
            throw new Error('Invalid token');
        }

        const user = await this.userRepository.getById(payload.userId);
        if (!user) {
            throw new Error('User not found');
        }

        const role = await this.roleRepository.getById(user.roleId);
        return UserDto.fromEntity(user, role);
    }
}

/**
 * User Service
 * Handles user management operations
 */
export class UserService {
    constructor() {
        this.userRepository = new UserRepository();
        this.roleRepository = new RoleRepository();
    }

    /**
     * Get user by ID
     * @param {number} userId - User ID
     * @returns {Object} User DTO
     */
    async getUserById(userId) {
        const user = await this.userRepository.getById(userId);
        if (!user) {
            throw new Error('User not found');
        }

        const role = await this.roleRepository.getById(user.roleId);
        return UserDto.fromEntity(user, role);
    }

    /**
     * Get all users (admin only)
     * @param {number} currentUserId - Current user ID
     * @returns {Array<Object>} User DTOs
     */
    async getAllUsers(currentUserId) {
        const currentUser = await this.userRepository.getById(currentUserId);
        if (currentUser.roleId !== UserRole.ADMIN) {
            throw new Error('Unauthorized: Admin access required');
        }

        const users = await this.userRepository.getAll();
        const roles = await this.roleRepository.getAll();
        
        return users.map(user => {
            const role = roles.find(r => r.id === user.roleId);
            return UserDto.fromEntity(user, role);
        });
    }
}
