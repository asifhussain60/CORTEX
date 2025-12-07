using MediatR;
using AutoMapper;
using Cortex.Clean.Domain.Interfaces;
using Cortex.Clean.Application.Queries;
using Cortex.Clean.Application.DTOs;

namespace Cortex.Clean.Application.Handlers;

/// <summary>
/// Handler for GetTasksQuery.
/// </summary>
public class GetTasksQueryHandler : IRequestHandler<GetTasksQuery, IEnumerable<TaskDto>>
{
    private readonly ITaskRepository _repository;
    private readonly IMapper _mapper;

    public GetTasksQueryHandler(ITaskRepository repository, IMapper mapper)
    {
        _repository = repository;
        _mapper = mapper;
    }

    public async Task<IEnumerable<TaskDto>> Handle(GetTasksQuery request, CancellationToken cancellationToken)
    {
        var tasks = await _repository.GetAllAsync(request.Filter, cancellationToken);
        return _mapper.Map<IEnumerable<TaskDto>>(tasks);
    }
}

/// <summary>
/// Handler for GetTaskByIdQuery.
/// </summary>
public class GetTaskByIdQueryHandler : IRequestHandler<GetTaskByIdQuery, TaskDto?>
{
    private readonly ITaskRepository _repository;
    private readonly IMapper _mapper;

    public GetTaskByIdQueryHandler(ITaskRepository repository, IMapper mapper)
    {
        _repository = repository;
        _mapper = mapper;
    }

    public async Task<TaskDto?> Handle(GetTaskByIdQuery request, CancellationToken cancellationToken)
    {
        var task = await _repository.GetByIdAsync(request.Id, cancellationToken);
        return task == null ? null : _mapper.Map<TaskDto>(task);
    }
}
