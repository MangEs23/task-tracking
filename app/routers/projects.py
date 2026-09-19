from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.dependencies import get_db, get_current_user
from app.models import User, Project, ProjectMember
from app.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectDetailResponse,
    ProjectUpdate,
    MemberAdd,
    MemberRoleUpdate,
    ProjectMemberResponse
)

router = APIRouter(prefix="/projects", tags=["Projects"])


def verify_project_admin(project_id: UUID, user_id: UUID, db: Session) -> ProjectMember:
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you are not a member"
        )
    
    if membership.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project admin can perform this action"
        )
    
    return membership


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_project = Project(
            name=project_in.name,
            description=project_in.description,
            created_by=current_user.id
        )
        db.add(new_project)
        db.flush()

        new_member = ProjectMember(
            project_id=new_project.id,
            user_id=current_user.id,
            role="admin"
        )
        db.add(new_member)

        db.commit()
        db.refresh(new_project)
        return new_project
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat proyek: {str(e)}"
        )


@router.get("", response_model=List[ProjectListResponse], status_code=status.HTTP_200_OK)
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    memberships = db.query(ProjectMember).filter(ProjectMember.user_id == current_user.id).all()
    result = []
    for m in memberships:
        project = m.project
        result.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "my_role": m.role,
            "member_count": len(project.members),
            "created_at": project.created_at
        })
    return result


@router.get("/{project_id}", response_model=ProjectDetailResponse, status_code=status.HTTP_200_OK)
def get_project_detail(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you are not a member"
        )

    project = db.query(Project).filter(Project.id == project_id).first()
    members_list = [
        {
            "user_id": m.user_id,
            "name": m.user.name,
            "email": m.user.email,
            "role": m.role
        } for m in project.members
    ]

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_by": project.created_by,
        "created_at": project.created_at,
        "members": members_list
    }


@router.patch("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Guard: Hanya admin project yang boleh update
    verify_project_admin(project_id, current_user.id, db)

    project = db.query(Project).filter(Project.id == project_id).first()
    
    if project_in.name is not None:
        project.name = project_in.name
    if project_in.description is not None:
        project.description = project_in.description

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Guard: Hanya admin project yang boleh delete
    verify_project_admin(project_id, current_user.id, db)

    project = db.query(Project).filter(Project.id == project_id).first()
    
    # Hapus anggota terlebih dahulu, kemudian hapus project
    db.query(ProjectMember).filter(ProjectMember.project_id == project_id).delete()
    db.delete(project)
    db.commit()
    return None


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: UUID,
    member_in: MemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Guard: Hanya admin project yang boleh mengundang member
    verify_project_admin(project_id, current_user.id, db)

    # Cari user berdasarkan email
    target_user = db.query(User).filter(User.email == member_in.email).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    existing_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == target_user.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project"
        )

    new_member = ProjectMember(
        project_id=project_id,
        user_id=target_user.id,
        role=member_in.role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return {
        "user_id": target_user.id,
        "name": target_user.name,
        "email": target_user.email,
        "role": new_member.role
    }


@router.patch("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse, status_code=status.HTTP_200_OK)
def update_member_role(
    project_id: UUID,
    user_id: UUID,
    role_in: MemberRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_project_admin(project_id, current_user.id, db)

    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this project"
        )

    member.role = role_in.role
    db.commit()
    db.refresh(member)

    return {
        "user_id": member.user.id,
        "name": member.user.name,
        "email": member.user.email,
        "role": member.role
    }


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_project_admin(project_id, current_user.id, db)

    if user_id == current_user.id:
        admin_count = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.role == "admin"
        ).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove yourself as the last admin of the project"
            )

    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this project"
        )

    db.delete(member)
    db.commit()
    return None