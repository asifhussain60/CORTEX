/**
 * Authentication Form Component
 * Handles login and registration forms
 * 
 * @module presentation/components/auth-form
 * @author Asif Hussain
 * @version 1.0.0
 */

import { AuthService } from '../../application/services.js';
import { LoginDto, RegisterDto } from '../../application/dtos.js';
import { StorageService } from '../../utils/storage.js';
import { Logger } from '../../utils/logger.js';

export class AuthForm {
    constructor() {
        this.authService = new AuthService();
        this.storageService = new StorageService();
        this.logger = new Logger('AuthForm');
        this.isLoginMode = true;
    }

    /**
     * Render the authentication form
     * @param {HTMLElement} container - Container element
     */
    render(container) {
        container.innerHTML = `
            <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
                <div class="max-w-md w-full space-y-8">
                    <div>
                        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                            Cortex-SDD Task Manager
                        </h2>
                        <p class="mt-2 text-center text-sm text-gray-600">
                            ${this.isLoginMode ? 'Sign in to your account' : 'Create a new account'}
                        </p>
                    </div>
                    <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                        <form id="auth-form" class="space-y-6">
                            ${this.renderFormFields()}
                            <div>
                                <button type="submit" 
                                    class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    ${this.isLoginMode ? 'Sign in' : 'Register'}
                                </button>
                            </div>
                            <div class="text-center">
                                <button type="button" id="toggle-mode" class="text-sm text-indigo-600 hover:text-indigo-500">
                                    ${this.isLoginMode ? "Don't have an account? Register" : 'Already have an account? Sign in'}
                                </button>
                            </div>
                        </form>
                        <div id="error-message" class="hidden mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                            <span class="block sm:inline" id="error-text"></span>
                        </div>
                        <div id="loading" class="hidden mt-4 text-center">
                            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Render form fields based on mode
     * @returns {string} HTML string
     */
    renderFormFields() {
        if (this.isLoginMode) {
            return `
                <div>
                    <label for="usernameOrEmail" class="block text-sm font-medium text-gray-700">
                        Username or Email
                    </label>
                    <input id="usernameOrEmail" name="usernameOrEmail" type="text" required
                        class="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Username or Email">
                </div>
                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700">
                        Password
                    </label>
                    <input id="password" name="password" type="password" required
                        class="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Password">
                </div>
            `;
        } else {
            return `
                <div>
                    <label for="username" class="block text-sm font-medium text-gray-700">
                        Username
                    </label>
                    <input id="username" name="username" type="text" required
                        class="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Username">
                </div>
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">
                        Email
                    </label>
                    <input id="email" name="email" type="email" required
                        class="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Email address">
                </div>
                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700">
                        Password
                    </label>
                    <input id="password" name="password" type="password" required
                        class="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Password (min 6 chars, 1 uppercase, 1 number)">
                </div>
                <div>
                    <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
                        Confirm Password
                    </label>
                    <input id="confirmPassword" name="confirmPassword" type="password" required
                        class="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Confirm password">
                </div>
            `;
        }
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const form = document.getElementById('auth-form');
        const toggleButton = document.getElementById('toggle-mode');

        form.addEventListener('submit', (e) => this.handleSubmit(e));
        toggleButton.addEventListener('click', () => this.toggleMode());
    }

    /**
     * Toggle between login and registration modes
     */
    toggleMode() {
        this.isLoginMode = !this.isLoginMode;
        const container = document.querySelector('.min-h-screen').parentElement;
        this.render(container);
    }

    /**
     * Handle form submission
     * @param {Event} event - Form submit event
     */
    async handleSubmit(event) {
        event.preventDefault();
        this.hideError();
        this.showLoading();

        try {
            if (this.isLoginMode) {
                await this.handleLogin();
            } else {
                await this.handleRegistration();
            }
        } catch (error) {
            this.logger.error('Authentication failed', error);
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Handle login submission
     */
    async handleLogin() {
        const usernameOrEmail = document.getElementById('usernameOrEmail').value;
        const password = document.getElementById('password').value;

        const loginDto = LoginDto.create(usernameOrEmail, password);
        const result = await this.authService.login(loginDto);

        // Store authentication data
        this.storageService.setItem('authToken', result.token);
        this.storageService.setItem('currentUser', result.user);

        this.logger.info('Login successful', result.user);

        // Redirect to main application
        window.location.href = 'index.html';
    }

    /**
     * Handle registration submission
     */
    async handleRegistration() {
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        const registerDto = RegisterDto.create({
            username,
            email,
            password,
            confirmPassword
        });

        const result = await this.authService.register(registerDto);

        // Store authentication data
        this.storageService.setItem('authToken', result.token);
        this.storageService.setItem('currentUser', result.user);

        this.logger.info('Registration successful', result.user);

        // Redirect to main application
        window.location.href = 'index.html';
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        const errorDiv = document.getElementById('error-message');
        const errorText = document.getElementById('error-text');
        errorText.textContent = message;
        errorDiv.classList.remove('hidden');
    }

    /**
     * Hide error message
     */
    hideError() {
        const errorDiv = document.getElementById('error-message');
        errorDiv.classList.add('hidden');
    }

    /**
     * Show loading spinner
     */
    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
    }

    /**
     * Hide loading spinner
     */
    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }
}
