"""
app/infrastructure/mappers/project_mapper.py
────────────────────────────────────────────
Bidirectional mapper between Project entity and ProjectModel ORM.
"""

from app.domain.entities.project import Project
from app.infrastructure.persistence.models.project_model import ProjectModel


class ProjectMapper:
    """Converts between Project (domain) ↔ ProjectModel (ORM)."""

    @staticmethod
    def to_entity(model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            owner_id=model.owner_id,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: Project) -> ProjectModel:
        return ProjectModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            owner_id=entity.owner_id,
            created_at=entity.created_at,
        )
