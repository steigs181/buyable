from flask_app.config.mysqlconnection import connectToMySQL

class MyCart:
    DB = "buyable_schema"
    
    def __init__(self, data):
        self.id = data['id']
        self.quantity = data['quanity']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
        self.item_id = data['item_id']
        self.item_name= data['name']
        self.item_price= data['price']
        self.item_img= data['img']
        self.item_total=self.item_price*self.quantity
        
        self.item_total_str='${:,.2f}'.format(self.item_total)
        if self.item_total==0:
            self.item_total_str="Free";
        self.item_price_str='${:,.2f}'.format(self.item_price)
        if self.item_price==0:
            self.item_price_str="Free";
            
        #print(self.item_price_str)
        
        #self.item_name =  data['items.name']

    @classmethod
    def get_all_by_user(cls,id):
        query = "SELECT * FROM shopping_cart LEFT JOIN items ON item_id=items.id WHERE shopping_cart.user_id=%(id)s;"
        data={"id": id}
        results = connectToMySQL(cls.DB).query_db(query,data)
        if not results:
            return []
        items = []
        for item in results:
            items.append(cls(item))
        return items
        
    @classmethod
    def get_all_by_user_total(cls,id):
        total=0
        query = "SELECT * FROM shopping_cart LEFT JOIN items ON item_id=items.id WHERE shopping_cart.user_id=%(id)s;"
        data={"id": id}
        results = connectToMySQL(cls.DB).query_db(query,data)
        if not results:
            return 0
        items = []
        for item in results:
            total+=cls(item).item_total
            print(f"[Item] {cls(item).item_name} (x{cls(item).quantity}):",cls(item).item_total)
        print(f"[Item] Total: {total}")
        return total;
    
    @classmethod
    def update(cls, data):
        query = """
            UPDATE shopping_cart
            SET quantity = %(quantity)s
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete(cls, id):
        query = """
            DELETE FROM shopping_cart WHERE id = %(id)s;
        """
        data = {"id": id}
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete_by_user(cls, id, user_id):
        query = """
            DELETE FROM shopping_cart WHERE id = %(id)s AND user_id = %(user_id)s;
        """
        data = {"id": id, "user_id": user_id}
        return connectToMySQL(cls.DB).query_db(query, data)
        
    @classmethod
    def clear(cls, id):
        query = """
            DELETE FROM shopping_cart WHERE user_id = %(id)s;
        """
        data = {"id": id}
        return connectToMySQL(cls.DB).query_db(query, data)
        
    @classmethod
    def check_in_cart(cls,item_id,user_id):
        loc_id=None;
        query = "SELECT * FROM shopping_cart WHERE user_id= %(user_id)s AND item_id=%(item_id)s;"
        data={"user_id": user_id, "item_id": item_id}
        results = connectToMySQL(cls.DB).query_db(query,data)
        if not results:
            return None;
        items = []
        if len(results)>0:
            loc_id=results[0]['id']
        return loc_id
        
    @classmethod
    def save(cls, data):
        query = """
            INSERT INTO shopping_cart (item_id,quanity,user_id)
            VALUES (%(item_id)s,%(quanity)s,%(user_id)s);
        """
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result
    
    @classmethod
    def update(cls, data):
        query = """
            UPDATE shopping_cart
            SET quanity = quanity+%(quanity)s, updated_at=NOW()
            WHERE item_id = %(item_id)s AND user_id=%(user_id)s;
        """
        return connectToMySQL(cls.DB).query_db(query, data)