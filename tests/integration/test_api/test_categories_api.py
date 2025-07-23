from fastapi import status


class TestCategoriesAPI:
    """Test suite for Categories API endpoints"""
    
    def test_get_all_categories_with_details_success(self, test_client, test_data_setup):
        """Test successful retrieval of all categories with subcategories"""

        response = test_client.get("/api/v1/categories/all_details")
        
        assert response.status_code == status.HTTP_200_OK
        
        categories = response.json()
        
        assert isinstance(categories, list)
        assert len(categories) == 2 
        
        food_category = categories[0] 
        assert food_category["name"] == "Food & Drinks"
        assert food_category["description"] == "Eating out, delivery, etc."
        assert food_category["display_order"] == 1
        assert "id" in food_category
        
        subcategories = food_category["subcategories"] 
        assert isinstance(subcategories, list)
        assert len(subcategories) == 2  
        
        coffee_subcat = subcategories[0] 
        assert coffee_subcat["name"] == "Tea & Coffee"
        assert coffee_subcat["icon_name"] == "emoji:☕"
        assert coffee_subcat["display_order"] == 1
        assert coffee_subcat["is_reimbursable"] is False
        assert coffee_subcat["exclude_from_budget"] is False
        assert coffee_subcat["parent_category_id"] == food_category["id"]
        
        transport_category = categories[1]
        assert transport_category["name"] == "Transport"
        assert transport_category["display_order"] == 2
        assert len(transport_category["subcategories"]) == 1
        
        uber_subcat = transport_category["subcategories"][0]
        assert uber_subcat["name"] == "Uber"
        assert uber_subcat["icon_name"] == "img:brand/uber.svg"
    
    def test_get_all_categories_ordering(self, test_client, test_data_setup):
        """Test that categories are returned in display_order"""
        
        response = test_client.get("/api/v1/categories/all_details")
        
        categories = response.json()
        
        assert categories[0]["display_order"] == 1 
        assert categories[1]["display_order"] == 2 
        
        food_subcats = categories[0]["subcategories"]
        assert food_subcats[0]["display_order"] == 1 
        assert food_subcats[1]["display_order"] == 2 
    
    def test_get_all_categories_empty_database(self, test_client):
        """Test response when no categories exist"""
        
        response = test_client.get("/api/v1/categories/all_details")
        
        assert response.status_code == status.HTTP_200_OK
        categories = response.json()
        assert categories == [] 
    
    def test_get_all_categories_response_schema(self, test_client, test_data_setup):
        """Test that response matches expected schema structure"""
        response = test_client.get("/api/v1/categories/all_details")
        
        categories = response.json()
        
        for category in categories:
            assert "id" in category
            assert "name" in category
            assert "display_order" in category
            assert "subcategories" in category
            
            assert "description" in category 
            
            assert isinstance(category["id"], int)
            assert isinstance(category["name"], str)
            assert isinstance(category["display_order"], int)
            assert isinstance(category["subcategories"], list)
            
            for subcategory in category["subcategories"]:
                assert "id" in subcategory
                assert "name" in subcategory
                assert "icon_name" in subcategory
                assert "display_order" in subcategory
                assert "is_reimbursable" in subcategory
                assert "exclude_from_budget" in subcategory
                assert "parent_category_id" in subcategory
                
                assert isinstance(subcategory["id"], int)
                assert isinstance(subcategory["name"], str)
                assert isinstance(subcategory["display_order"], int)
                assert isinstance(subcategory["is_reimbursable"], bool)
                assert isinstance(subcategory["exclude_from_budget"], bool)
                assert isinstance(subcategory["parent_category_id"], int)
                
                assert subcategory["parent_category_id"] == category["id"]

    # TODO: Add tests for other categories endpoints:
    # - GET /api/v1/categories/{category_id_or_name}
    # - GET /api/v1/categories/subcategories/{subcategory_id}
    # - Error cases (404s, invalid IDs)