using MediatR;
using AutoMapper;
using Cortex.Clean.Domain.Entities;
using Cortex.Clean.Domain.Interfaces;
using Cortex.Clean.Application.Commands;
using Cortex.Clean.Application.DTOs;

namespace Cortex.Clean.Application.Handlers;

/// <summary>
/// Handler for CreateTaskCommand.
/// </summary>
public class CreateTaskCommandHandler : IRequestHandler<CreateTaskCommand, TaskDto>
{
    private readonly ITaskRepository _repository;
    private readonly IMapper _mapper;

    public CreateTaskCommandHandler(ITaskRepository repository, IMapper mapper)
    {
        _repository = repository;
        _mapper = mapper;
    }

    public async Task<TaskDto> Handle(CreateTaskCommand request, CancellationToken cancellationToken)
    {
        var task = new TaskEntity(request.Title);
        var created = await _repository.AddAsync(task, cancellationToken);
        await _repository.SaveChangesAsync(cancellationToken);
        return _mapper.Map<TaskDto>(created);
    }
}

/// <summary>
/// Handler for UpdateTaskCommand.
/// </summary>
public class UpdateTaskCommandHandler : IRequestHandler<UpdateTaskCommand, Unit>
{
    private readonly ITaskRepository _repository;

    public UpdateTaskCommandHandler(ITaskRepository repository)
    {
        _repository = repository;
    }

    public async Task<Unit> Handle(UpdateTaskCommand request, CancellationToken cancellationToken)
    {
        var task = await _repository.GetByIdAsync(request.Id, cancellationToken);
        if (task == null)
            throw new KeyNotFoundException($"Task with ID {request.Id} not found.");

        task.UpdateTitle(request.Title);
        if (task.IsCompleted != request.IsCompleted)
            task.ToggleCompletion();

        await _repository.UpdateAsync(task, cancellationToken);
        await _repository.SaveChangesAsync(cancellationToken);
        return Unit.Value;
    }
}

/// <summary>
/// Handler for DeleteTaskCommand.
/// </summary>
public class DeleteTaskCommandHandler : IRequestHandler<DeleteTaskCommand, bool>
{
    private readonly ITaskRepository _repository;

    public DeleteTaskCommandHandler(ITaskRepository repository)
    {
        _repository = repository;
    }

    public async Task<bool> Handle(DeleteTaskCommand request, CancellationToken cancellationToken)
    {
        var result = await _repository.DeleteAsync(request.Id, cancellationToken);
        if (result)
            await _repository.SaveChangesAsync(cancellationToken);
        return result;
    }
}

/// <summary>
/// Handler for ToggleTaskCompletionCommand.
/// </summary>
public class ToggleTaskCompletionCommandHandler : IRequestHandler<ToggleTaskCompletionCommand, Unit>
{
    private readonly ITaskRepository _repository;

    public ToggleTaskCompletionCommandHandler(ITaskRepository repository)
    {
        _repository = repository;
    }

    public async Task<Unit> Handle(ToggleTaskCompletionCommand request, CancellationToken cancellationToken)
    {
        var task = await _repository.GetByIdAsync(request.Id, cancellationToken);
        if (task == null)
            throw new KeyNotFoundException($"Task with ID {request.Id} not found.");

        task.ToggleCompletion();
        await _repository.UpdateAsync(task, cancellationToken);
        await _repository.SaveChangesAsync(cancellationToken);
        return Unit.Value;
    }
}
