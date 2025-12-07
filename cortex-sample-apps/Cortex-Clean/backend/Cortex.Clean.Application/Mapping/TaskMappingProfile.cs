using AutoMapper;
using Cortex.Clean.Domain.Entities;
using Cortex.Clean.Application.DTOs;

namespace Cortex.Clean.Application.Mapping;

/// <summary>
/// AutoMapper profile for Task entity mappings.
/// </summary>
public class TaskMappingProfile : Profile
{
    public TaskMappingProfile()
    {
        CreateMap<TaskEntity, TaskDto>();
        CreateMap<CreateTaskRequest, TaskEntity>()
            .ConstructUsing(src => new TaskEntity(src.Title));
    }
}
