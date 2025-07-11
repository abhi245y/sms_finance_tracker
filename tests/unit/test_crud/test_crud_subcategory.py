from tests.fixtures.test_data_factory import TestDataFactory
from app.crud import crud_subcategory
from app.schemas.category import SubCategoryCreate, SubCategoryUpdate

class TestSubCategoryCRUD:
    
    def test_create_subcategory_success(self, db_session):
       
        parent_category = TestDataFactory.create_test_category(db_session, name="Shopping")
        
        subcategory_data = SubCategoryCreate(
            name="Electronics",
            icon_name="fthr:smartphone",
            display_order=1,
            is_reimbursable=False,
            exclude_from_budget=False,
            parent_category_id=parent_category.id
        )
        
       
        result = crud_subcategory.create_subcategory(db_session, obj_in=subcategory_data)
        
        
        assert result.id is not None
        assert result.name == "Electronics"
        assert result.parent_category_id == parent_category.id
        assert result.is_reimbursable is False
    
    def test_get_subcategory_with_parent(self, db_session):
       
        parent_category = TestDataFactory.create_test_category(db_session, name="Bills")
        subcategory = TestDataFactory.create_test_sub_category(
            db_session, parent_category, name="Electricity"
        )
        
       
        result = crud_subcategory.get_subcategory(db_session, subcategory_id=subcategory.id)
        
        
        assert result is not None
        assert result.name == "Electricity"
        assert result.parent_category is not None
        assert result.parent_category.name == "Bills"
    
    def test_get_subcategories_for_parent(self, db_session):
       
        parent_category = TestDataFactory.create_test_category(db_session, name="Entertainment")
        subcategory1 = TestDataFactory.create_test_sub_category(
            db_session, parent_category, name="Movies", display_order=1
        )
        subcategory2 = TestDataFactory.create_test_sub_category(
            db_session, parent_category, name="Games", display_order=2
        )
        
       
        result = crud_subcategory.get_subcategories_for_parent(
            db_session, parent_category_id=parent_category.id
        )
        
        
        assert len(result) == 2
        assert result[0].display_order <= result[1].display_order
        result_ids = [sub.id for sub in result]
        assert subcategory1.id in result_ids
        assert subcategory2.id in result_ids
    
        if result[0].id == subcategory1.id:
            assert result[1].id == subcategory2.id
        else:
            assert result[0].id == subcategory2.id
            assert result[1].id == subcategory1.id
    
    def test_update_subcategory_flags(self, db_session):
       
        parent_category = TestDataFactory.create_test_category(db_session)
        subcategory = TestDataFactory.create_test_sub_category(
            db_session, parent_category, is_reimbursable=False, exclude_from_budget=False
        )
        
       
        update_data = SubCategoryUpdate(is_reimbursable=True, exclude_from_budget=True)
        updated_subcategory = crud_subcategory.update_subcategory(
            db_session, db_obj=subcategory, obj_in=update_data
        )
        
        
        assert updated_subcategory.is_reimbursable is True
        assert updated_subcategory.exclude_from_budget is True
        assert updated_subcategory.id == subcategory.id