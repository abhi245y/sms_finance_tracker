from tests.fixtures.test_data_factory import TestDataFactory
from app.crud import crud_category
from app.schemas.category import CategoryCreate

class TestCategoryCRUD:
    
    def test_create_category(self, db_session):
        category_data = CategoryCreate(
            name="Test Transport",
            description="All transport related expenses",
            display_order=5
        )
        
        result = crud_category.create_category(db_session, obj_in=category_data)
        print(result)
        assert result.id is not None
        assert result.name == "Test Transport"
        assert result.description == "All transport related expenses"
        assert result.display_order == 5
    
    def test_get_category_by_name_exists(self, db_session):
        category = TestDataFactory.create_test_category(
            db_session, name="Unique Category Name"
        )
        
        result = crud_category.get_category_by_name(db_session, name="Unique Category Name")
        
        assert result is not None
        assert result.id == category.id
        assert result.name == "Unique Category Name"
    
    def test_get_category_by_name_not_found(self, db_session):
        
        result = crud_category.get_category_by_name(db_session, name="Does Not Exist")
        
        assert result is None
    
    def test_get_categories_with_subcategories(self, db_session):
        category = TestDataFactory.create_test_category(db_session, name="Food")
        subcategory1 = TestDataFactory.create_test_sub_category(
            db_session, category, name="Pizza"
        )
        subcategory2 = TestDataFactory.create_test_sub_category(
            db_session, category, name="Coffee"
        )
        
        result = crud_category.get_categories(db_session, skip=0, limit=10)
        
        assert len(result) == 1
        category_result = result[0]
        assert category_result.name == "Food"
        assert len(category_result.subcategories) == 2
        
        subcategory_ids = [sub.id for sub in category_result.subcategories]
        assert subcategory1.id in subcategory_ids
        assert subcategory2.id in subcategory_ids
    
        subcategory_names = [sub.name for sub in category_result.subcategories]
        assert "Pizza" in subcategory_names
        assert "Coffee" in subcategory_names