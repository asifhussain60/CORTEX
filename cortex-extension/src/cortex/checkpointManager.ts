/**
 * CORTEX Checkpoint Manager - Conversation State Persistence
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Proprietary - See LICENSE file for terms
 */

import { BrainBridge } from './brainBridge';

export class CheckpointManager {
    private brainBridge: BrainBridge;
    private autoCheckpointInterval: NodeJS.Timeout | null = null;

    constructor(brainBridge: BrainBridge) {
        this.brainBridge = brainBridge;
    }

    startAutoCheckpoint(intervalMinutes: number = 10): void {
        this.autoCheckpointInterval = setInterval(async () => {
            try {
                await this.brainBridge.createCheckpoint();
                console.log('Auto-checkpoint created');
            } catch (error) {
                console.error('Auto-checkpoint failed:', error);
            }
        }, intervalMinutes * 60 * 1000);
    }

    stopAutoCheckpoint(): void {
        if (this.autoCheckpointInterval) {
            clearInterval(this.autoCheckpointInterval);
            this.autoCheckpointInterval = null;
        }
    }

    async createCheckpoint(): Promise<string> {
        return await this.brainBridge.createCheckpoint();
    }
}
