"use strict";
/**
 * CORTEX Checkpoint Manager - Conversation State Persistence
 *
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Proprietary - See LICENSE file for terms
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.CheckpointManager = void 0;
class CheckpointManager {
    constructor(brainBridge) {
        this.autoCheckpointInterval = null;
        this.brainBridge = brainBridge;
    }
    startAutoCheckpoint(intervalMinutes = 10) {
        this.autoCheckpointInterval = setInterval(async () => {
            try {
                await this.brainBridge.createCheckpoint();
                console.log('Auto-checkpoint created');
            }
            catch (error) {
                console.error('Auto-checkpoint failed:', error);
            }
        }, intervalMinutes * 60 * 1000);
    }
    stopAutoCheckpoint() {
        if (this.autoCheckpointInterval) {
            clearInterval(this.autoCheckpointInterval);
            this.autoCheckpointInterval = null;
        }
    }
    async createCheckpoint() {
        return await this.brainBridge.createCheckpoint();
    }
}
exports.CheckpointManager = CheckpointManager;
//# sourceMappingURL=checkpointManager.js.map