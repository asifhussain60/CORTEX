/**
 * Data Transfer Objects (DTOs)
 * Clean data contracts for API communication
 * 
 * @module application/dtos
 * @author Asif Hussain
 * @version 1.0.0
 */

/**
 * Task DTO Factory
 */
export const TaskDto = {
    /**
     * Create a new task DTO
     * @param {Object} data - Task data
     * @returns {Object} Task DTO
     */
    create(data = {}) {
        return {
            id: data.id || null,
            title: data.title || '',
            isCompleted: data.isCompleted || false,
            createdAt: data.createdAt || null,
            updatedAt: data.updatedAt || null,
            userId: data.userId || null,
            userName: data.userName || null
        };
    },

    /**
     * Map Task entity to DTO
     * @param {Task} task - Task entity
     * @param {User} user - Optional user entity
     * @returns {Object} Task DTO
     */
    fromEntity(task, user = null) {
        return {
            id: task.id,
            title: task.title,
            isCompleted: task.isCompleted,
            createdAt: task.createdAt,
            updatedAt: task.updatedAt,
            userId: task.userId,
            userName: user ? user.username : null
        };
    },

    /**
     * Map DTO to Task entity data
     * @param {Object} dto - Task DTO
     * @returns {Object} Task entity data
     */
    toEntity(dto) {
        return {
            title: dto.title,
            isCompleted: dto.isCompleted || false,
            userId: dto.userId
        };
    }
};

/**
 * User DTO Factory
 */
export const UserDto = {
    /**
     * Create a new user DTO
     * @param {Object} data - User data
     * @returns {Object} User DTO
     */
    create(data = {}) {
        return {
            id: data.id || null,
            username: data.username || '',
            email: data.email || '',
            roleName: data.roleName || 'User',
            createdAt: data.createdAt || null
        };
    },

    /**
     * Map User entity to DTO (excludes password)
     * @param {User} user - User entity
     * @param {Role} role - Optional role entity
     * @returns {Object} User DTO
     */
    fromEntity(user, role = null) {
        return {
            id: user.id,
            username: user.username,
            email: user.email,
            roleName: role ? role.name : 'User',
            createdAt: user.createdAt
        };
    }
};

/**
 * Login Request DTO
 */
export const LoginDto = {
    /**
     * Create login DTO
     * @param {string} usernameOrEmail - Username or email
     * @param {string} password - Password
     * @returns {Object} Login DTO
     */
    create(usernameOrEmail, password) {
        return {
            usernameOrEmail: usernameOrEmail || '',
            password: password || ''
        };
    }
};

/**
 * Register Request DTO
 */
export const RegisterDto = {
    /**
     * Create register DTO
     * @param {Object} data - Registration data
     * @returns {Object} Register DTO
     */
    create(data = {}) {
        return {
            username: data.username || '',
            email: data.email || '',
            password: data.password || '',
            confirmPassword: data.confirmPassword || ''
        };
    }
};

/**
 * Authentication Response DTO
 */
export const AuthResponseDto = {
    /**
     * Create auth response DTO
     * @param {Object} user - User DTO
     * @param {string} token - JWT token
     * @returns {Object} Auth response DTO
     */
    create(user, token) {
        return {
            user: user,
            token: token,
            expiresAt: new Date(Date.now() + 15 * 60 * 1000).toISOString() // 15 minutes
        };
    }
};

/**
 * Task Filter DTO
 */
export const TaskFilterDto = {
    /**
     * Create task filter DTO
     * @param {Object} filters - Filter criteria
     * @returns {Object} Task filter DTO
     */
    create(filters = {}) {
        return {
            userId: filters.userId || null,
            isCompleted: filters.isCompleted !== undefined ? filters.isCompleted : null,
            searchTerm: filters.searchTerm || ''
        };
    }
};
