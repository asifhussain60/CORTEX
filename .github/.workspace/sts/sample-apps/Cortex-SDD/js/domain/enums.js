/**
 * Domain Enums
 * Defines enumeration types for the task management domain
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

/**
 * Task Priority Levels
 * @readonly
 * @enum {number}
 */
export const Priority = Object.freeze({
    Low: 1,
    Medium: 2,
    High: 3,
    Critical: 4
});

/**
 * Get priority name from value
 * @param {number} value - Priority value
 * @returns {string} Priority name
 */
export function getPriorityName(value) {
    const entry = Object.entries(Priority).find(([_, v]) => v === value);
    return entry ? entry[0] : 'Unknown';
}

/**
 * Task Status States
 * @readonly
 * @enum {number}
 */
export const Status = Object.freeze({
    Open: 1,
    InProgress: 2,
    Testing: 3,
    Completed: 4,
    Blocked: 5,
    Cancelled: 6
});

/**
 * Get status name from value
 * @param {number} value - Status value
 * @returns {string} Status name
 */
export function getStatusName(value) {
    const entry = Object.entries(Status).find(([_, v]) => v === value);
    return entry ? entry[0] : 'Unknown';
}

/**
 * User Roles
 * @readonly
 * @enum {number}
 */
export const Role = Object.freeze({
    User: 1,
    TeamLead: 2,
    Admin: 3
});

/**
 * Get role name from value
 * @param {number} value - Role value
 * @returns {string} Role name
 */
export function getRoleName(value) {
    const entry = Object.entries(Role).find(([_, v]) => v === value);
    return entry ? entry[0] : 'Unknown';
}

/**
 * Check if role has admin privileges
 * @param {number} roleValue - Role value
 * @returns {boolean} True if admin
 */
export function isAdmin(roleValue) {
    return roleValue === Role.Admin;
}

/**
 * Check if role has team lead privileges
 * @param {number} roleValue - Role value
 * @returns {boolean} True if team lead or admin
 */
export function isTeamLead(roleValue) {
    return roleValue === Role.TeamLead || roleValue === Role.Admin;
}

export default { Priority, Status, Role, getPriorityName, getStatusName, getRoleName, isAdmin, isTeamLead };
