from flask_app.config.mysqlconnection import connectToMySQL

class Sellers:
    DB = "buyable_schema"
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.items = None

    @classmethod
    def get_one(cls, seller_id):
        query = """
            SELECT * FROM sellers WHERE id=%(id)s;
        """
        data ={'id': seller_id}
        results = connectToMySQL(cls.DB).query_db(query, data)
        if (not len(results)):
            return None;
        return results[0];
    
    @classmethod
    def update(cls, data):
        query = """
            UPDATE sellers
            SET name = %(brand_name)s, description = %(brand_desc)s, updated_at=NOW()
            WHERE id = %(id)s AND user_id = %(user_id)s;
        """
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete(cls, id):
        query = "DELETE FROM sellers WHERE id = %(id)s;"
        data = {'id': id}
        return connectToMySQL(cls.DB).query_db(query,data)