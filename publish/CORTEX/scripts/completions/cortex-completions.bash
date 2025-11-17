#!/usr/bin/env bash
# CORTEX Shell Completions for Bash
# 
# Installation:
#   Source this file in your ~/.bashrc or ~/.bash_profile:
#   source /path/to/CORTEX/scripts/completions/cortex-completions.bash
#
# Or copy to system completions directory:
#   sudo cp cortex-completions.bash /etc/bash_completion.d/cortex
#
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.
# Phase: Phase 4.2 - Shell Integration

# Completion for cortex-capture
_cortex_capture() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="--type --tags --interactive --repo --help"
    types="feature bug refactor general"
    
    case "${prev}" in
        --type)
            COMPREPLY=( $(compgen -W "${types}" -- ${cur}) )
            return 0
            ;;
        --tags)
            # Could suggest common tags from history
            return 0
            ;;
        --repo)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
    
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

# Completion for cortex-bug
_cortex_bug() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="--severity --error --files --interactive --repo --help"
    severities="low medium high critical"
    
    case "${prev}" in
        --severity)
            COMPREPLY=( $(compgen -W "${severities}" -- ${cur}) )
            return 0
            ;;
        --files)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --repo)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
    
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

# Completion for cortex-feature
_cortex_feature() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="--components --tests --interactive --repo --help"
    
    case "${prev}" in
        --components)
            # Could suggest components from project structure
            return 0
            ;;
        --repo)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
    
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

# Completion for cortex-resume
_cortex_resume() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="--last --search --limit --interactive --repo --help"
    
    case "${prev}" in
        --last|--limit)
            COMPREPLY=( $(compgen -W "1 3 5 10" -- ${cur}) )
            return 0
            ;;
        --repo)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
    
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

# Completion for cortex-recall (new command)
_cortex_recall() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="--type --limit --format --repo --help"
    types="feature bug refactor general all"
    formats="short full json"
    
    case "${prev}" in
        --type)
            COMPREPLY=( $(compgen -W "${types}" -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "${formats}" -- ${cur}) )
            return 0
            ;;
        --limit)
            COMPREPLY=( $(compgen -W "5 10 20 50" -- ${cur}) )
            return 0
            ;;
        --repo)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
    
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

# Register completions
complete -F _cortex_capture cortex-capture
complete -F _cortex_bug cortex-bug
complete -F _cortex_feature cortex-feature
complete -F _cortex_resume cortex-resume
complete -F _cortex_recall cortex-recall

# Main cortex command completion (if exists)
_cortex() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Main cortex commands
    opts="capture bug feature resume recall setup status help"
    
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "--help --version" -- ${cur}) )
        return 0
    else
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

complete -F _cortex cortex

# Success message
echo "✅ CORTEX shell completions loaded (bash)"
