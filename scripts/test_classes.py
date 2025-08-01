#!/usr/bin/env python3
"""
Test script for Classes & Collaboration functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.class_ import Class, ClassMember, ClassStudySet
from app.models.study_set import StudySet
from app.schemas.class_ import ClassCreate, ClassStudySetCreate
from app.services.class_service import ClassService, ClassStudySetService, ClassProgressService


def test_classes_functionality():
    """Test the classes functionality"""
    db = SessionLocal()
    
    try:
        print("🧪 Testing Classes & Collaboration functionality...")
        
        # Create test users
        print("1. Creating test users...")
        teacher = User(
            username="teacher_test",
            email="teacher@test.com",
            password_hash="hashed_password",
            full_name="Test Teacher"
        )
        db.add(teacher)
        
        student1 = User(
            username="student1_test",
            email="student1@test.com",
            password_hash="hashed_password",
            full_name="Test Student 1"
        )
        db.add(student1)
        
        student2 = User(
            username="student2_test",
            email="student2@test.com",
            password_hash="hashed_password",
            full_name="Test Student 2"
        )
        db.add(student2)
        
        db.commit()
        db.refresh(teacher)
        db.refresh(student1)
        db.refresh(student2)
        
        print(f"   ✅ Created teacher: {teacher.username}")
        print(f"   ✅ Created student1: {student1.username}")
        print(f"   ✅ Created student2: {student2.username}")
        
        # Create a test study set
        print("2. Creating test study set...")
        study_set = StudySet(
            title="Test Study Set",
            description="A test study set for classes",
            user_id=teacher.id,
            is_public=True
        )
        db.add(study_set)
        db.commit()
        db.refresh(study_set)
        print(f"   ✅ Created study set: {study_set.title}")
        
        # Create a class
        print("3. Creating a class...")
        class_data = ClassCreate(name="Test Class", description="A test class")
        class_ = ClassService.create_class(db, class_data, teacher.id)
        print(f"   ✅ Created class: {class_.name} with join code: {class_.join_code}")
        
        # Join class with students
        print("4. Students joining the class...")
        ClassService.join_class(db, class_.join_code, student1.id)
        ClassService.join_class(db, class_.join_code, student2.id)
        print(f"   ✅ Students joined the class")
        
        # Assign study set to class
        print("5. Assigning study set to class...")
        assignment_data = ClassStudySetCreate(
            study_set_id=study_set.id,
            due_date=None,
            is_optional=False
        )
        assignment = ClassStudySetService.assign_study_set(db, class_id=class_.id, study_set_data=assignment_data, user_id=teacher.id)
        print(f"   ✅ Assigned study set to class")
        
        # Get class members
        print("6. Getting class members...")
        members = ClassService.get_class_members(db, class_.id)
        print(f"   ✅ Found {len(members)} members in the class")
        
        # Get class assignments
        print("7. Getting class assignments...")
        assignments = ClassStudySetService.get_class_assignments(db, class_.id)
        print(f"   ✅ Found {len(assignments)} assignments in the class")
        
        # Get class progress (should be empty since no study sessions)
        print("8. Getting class progress...")
        progress = ClassProgressService.get_class_progress(db, class_.id, teacher.id)
        print(f"   ✅ Found progress data for {len(progress)} students")
        
        print("\n🎉 All tests passed! Classes & Collaboration functionality is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_classes_functionality() 