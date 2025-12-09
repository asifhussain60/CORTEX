/**
 * Authentication Form Component
 * Handles login and registration forms
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Logger } from '../../utils/logger.js';
import { AuthService } from '../../application/services.js';

export class AuthFormComponent {
    constructor() {
        this.authService = new AuthService();
        this.currentMode = 'login'; // 'login' or 'register'
        Logger.debug('AuthFormComponent initialized');
    }

    /**
     * Render login form
     * @param {HTMLElement} container - Container element
     */
    renderLogin(container) {
        if (!container) {
            Logger.error('AuthFormComponent.renderLogin: container is null');
            return;
        }

        this.currentMode = 'login';
        container.innerHTML = `
            <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 p-4">
                <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
                    <!-- Logo/Title -->
                    <div class="text-center mb-8">
                        <h1 class="text-4xl font-bold text-gray-800 mb-2">Cortex-SDD</h1>
                        <p class="text-gray-600">Task Management System</p>
                    </div>

                    <!-- Login Form -->
                    <form id="login-form" class="space-y-6">
                        <!-- Username Field -->
                        <div>
                            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                                Username
                            </label>
                            <input 
                                type="text" 
                                id="username" 
                                name="username"
                                required
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                placeholder="Enter your username"
                            />
                            <span class="text-red-500 text-sm hidden" id="username-error"></span>
                        </div>

                        <!-- Password Field -->
                        <div>
                            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                                Password
                            </label>
                            <input 
                                type="password" 
                                id="password" 
                                name="password"
                                required
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                placeholder="Enter your password"
                            />
                            <span class="text-red-500 text-sm hidden" id="password-error"></span>
                        </div>

                        <!-- Error Message -->
                        <div id="form-error" class="hidden bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                        </div>

                        <!-- Submit Button -->
                        <button 
                            type="submit"
                            id="submit-btn"
                            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition-colors duration-200 flex items-center justify-center"
                        >
                            <span id="submit-text">Sign In</span>
                            <span id="submit-spinner" class="hidden ml-2">
                                <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            </span>
                        </button>
                    </form>

                    <!-- Toggle to Register -->
                    <div class="mt-6 text-center">
                        <p class="text-gray-600 text-sm">
                            Don't have an account? 
                            <button 
                                id="toggle-register" 
                                class="text-blue-600 hover:text-blue-800 font-medium"
                            >
                                Register here
                            </button>
                        </p>
                    </div>

                    <!-- Demo Credentials -->
                    <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                        <p class="text-xs font-medium text-gray-700 mb-2">Demo Credentials:</p>
                        <div class="text-xs text-gray-600 space-y-1">
                            <div><strong>Admin:</strong> admin / Admin@123</div>
                            <div><strong>Team Lead:</strong> teamlead / TeamLead@123</div>
                            <div><strong>User:</strong> user / User@123</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this._attachLoginHandlers(container);
    }

    /**
     * Render registration form
     * @param {HTMLElement} container - Container element
     */
    renderRegister(container) {
        if (!container) {
            Logger.error('AuthFormComponent.renderRegister: container is null');
            return;
        }

        this.currentMode = 'register';
        container.innerHTML = `
            <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-600 p-4">
                <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
                    <!-- Logo/Title -->
                    <div class="text-center mb-8">
                        <h1 class="text-4xl font-bold text-gray-800 mb-2">Join Cortex-SDD</h1>
                        <p class="text-gray-600">Create your account</p>
                    </div>

                    <!-- Registration Form -->
                    <form id="register-form" class="space-y-4">
                        <!-- Username Field -->
                        <div>
                            <label for="reg-username" class="block text-sm font-medium text-gray-700 mb-2">
                                Username
                            </label>
                            <input 
                                type="text" 
                                id="reg-username" 
                                name="username"
                                required
                                minlength="3"
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                placeholder="Choose a username"
                            />
                            <span class="text-red-500 text-sm hidden" id="reg-username-error"></span>
                        </div>

                        <!-- Email Field -->
                        <div>
                            <label for="reg-email" class="block text-sm font-medium text-gray-700 mb-2">
                                Email
                            </label>
                            <input 
                                type="email" 
                                id="reg-email" 
                                name="email"
                                required
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                placeholder="your.email@example.com"
                            />
                            <span class="text-red-500 text-sm hidden" id="reg-email-error"></span>
                        </div>

                        <!-- Password Field -->
                        <div>
                            <label for="reg-password" class="block text-sm font-medium text-gray-700 mb-2">
                                Password
                            </label>
                            <input 
                                type="password" 
                                id="reg-password" 
                                name="password"
                                required
                                minlength="8"
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                placeholder="Create a strong password"
                            />
                            <span class="text-xs text-gray-500">Min 8 characters, include uppercase, number, special char</span>
                            <span class="text-red-500 text-sm hidden block" id="reg-password-error"></span>
                        </div>

                        <!-- Confirm Password Field -->
                        <div>
                            <label for="reg-confirm-password" class="block text-sm font-medium text-gray-700 mb-2">
                                Confirm Password
                            </label>
                            <input 
                                type="password" 
                                id="reg-confirm-password" 
                                name="confirmPassword"
                                required
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                placeholder="Confirm your password"
                            />
                            <span class="text-red-500 text-sm hidden" id="reg-confirm-password-error"></span>
                        </div>

                        <!-- Error Message -->
                        <div id="form-error" class="hidden bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                        </div>

                        <!-- Submit Button -->
                        <button 
                            type="submit"
                            id="submit-btn"
                            class="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 rounded-lg transition-colors duration-200 flex items-center justify-center"
                        >
                            <span id="submit-text">Create Account</span>
                            <span id="submit-spinner" class="hidden ml-2">
                                <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            </span>
                        </button>
                    </form>

                    <!-- Toggle to Login -->
                    <div class="mt-6 text-center">
                        <p class="text-gray-600 text-sm">
                            Already have an account? 
                            <button 
                                id="toggle-login" 
                                class="text-purple-600 hover:text-purple-800 font-medium"
                            >
                                Sign in here
                            </button>
                        </p>
                    </div>
                </div>
            </div>
        `;

        this._attachRegisterHandlers(container);
    }

    /**
     * Attach login form handlers
     * @param {HTMLElement} container - Container element
     */
    _attachLoginHandlers(container) {
        const form = container.querySelector('#login-form');
        const toggleBtn = container.querySelector('#toggle-register');

        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this._handleLogin(e.target);
            });
        }

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.renderRegister(container.parentElement || container);
            });
        }
    }

    /**
     * Attach registration form handlers
     * @param {HTMLElement} container - Container element
     */
    _attachRegisterHandlers(container) {
        const form = container.querySelector('#register-form');
        const toggleBtn = container.querySelector('#toggle-login');

        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this._handleRegister(e.target);
            });
        }

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.renderLogin(container.parentElement || container);
            });
        }
    }

    /**
     * Handle login submission
     * @param {HTMLFormElement} form - Form element
     */
    async _handleLogin(form) {
        const formData = new FormData(form);
        const username = formData.get('username')?.trim();
        const password = formData.get('password');

        // Clear previous errors
        this._clearErrors();

        // Validate
        if (!username || !password) {
            this._showError('Please fill in all fields');
            return;
        }

        // Show loading state
        this._setLoading(true);

        try {
            // Call auth service
            const result = await this.authService.login(username, password);
            
            if (result.success) {
                Logger.info('Login successful');
                // Redirect to main page
                window.location.href = 'index.html';
            } else {
                this._showError(result.message || 'Invalid credentials');
            }
        } catch (error) {
            Logger.error('Login error:', error);
            this._showError(error.message || 'Login failed. Please try again.');
        } finally {
            this._setLoading(false);
        }
    }

    /**
     * Handle registration submission
     * @param {HTMLFormElement} form - Form element
     */
    async _handleRegister(form) {
        const formData = new FormData(form);
        const username = formData.get('username')?.trim();
        const email = formData.get('email')?.trim();
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');

        // Clear previous errors
        this._clearErrors();

        // Validate
        if (!username || !email || !password || !confirmPassword) {
            this._showError('Please fill in all fields');
            return;
        }

        if (password !== confirmPassword) {
            this._showFieldError('reg-confirm-password', 'Passwords do not match');
            return;
        }

        // Show loading state
        this._setLoading(true);

        try {
            // Call auth service
            const result = await this.authService.register(username, email, password);
            
            if (result.success) {
                Logger.info('Registration successful');
                // Show success message and switch to login
                this._showSuccess('Account created successfully! Please login.');
                setTimeout(() => {
                    this.renderLogin(form.closest('.min-h-screen').parentElement);
                }, 2000);
            } else {
                this._showError(result.message || 'Registration failed');
            }
        } catch (error) {
            Logger.error('Registration error:', error);
            this._showError(error.message || 'Registration failed. Please try again.');
        } finally {
            this._setLoading(false);
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    _showError(message) {
        const errorDiv = document.querySelector('#form-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        }
    }

    /**
     * Show success message
     * @param {string} message - Success message
     */
    _showSuccess(message) {
        const errorDiv = document.querySelector('#form-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden', 'bg-red-50', 'border-red-200', 'text-red-700');
            errorDiv.classList.add('bg-green-50', 'border-green-200', 'text-green-700');
        }
    }

    /**
     * Show field-specific error
     * @param {string} fieldId - Field ID
     * @param {string} message - Error message
     */
    _showFieldError(fieldId, message) {
        const errorSpan = document.querySelector(`#${fieldId}-error`);
        if (errorSpan) {
            errorSpan.textContent = message;
            errorSpan.classList.remove('hidden');
        }
    }

    /**
     * Clear all errors
     */
    _clearErrors() {
        const errorDiv = document.querySelector('#form-error');
        if (errorDiv) {
            errorDiv.classList.add('hidden');
            errorDiv.classList.remove('bg-green-50', 'border-green-200', 'text-green-700');
            errorDiv.classList.add('bg-red-50', 'border-red-200', 'text-red-700');
        }

        document.querySelectorAll('[id$="-error"]').forEach(span => {
            span.classList.add('hidden');
        });
    }

    /**
     * Set loading state
     * @param {boolean} isLoading - Loading state
     */
    _setLoading(isLoading) {
        const submitBtn = document.querySelector('#submit-btn');
        const submitText = document.querySelector('#submit-text');
        const submitSpinner = document.querySelector('#submit-spinner');

        if (submitBtn) {
            submitBtn.disabled = isLoading;
        }

        if (submitText) {
            submitText.classList.toggle('hidden', isLoading);
        }

        if (submitSpinner) {
            submitSpinner.classList.toggle('hidden', !isLoading);
        }
    }
}
