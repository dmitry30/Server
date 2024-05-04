import pypyodbc

class DbActions:
    def __init__(self):
        self.connection = pypyodbc.connect('Driver={SQL Server};'
                                      'Server=DESKTOP-DRJ2SPN;'
                                      'Database=Term;'
                                      'uid=python;'
                                      'pwd=pythonsa')

    def get_all_prices(self):
        cursor = self.connection.cursor()
        cursor.execute("""select pr.Guid as ProductGuid, avg(p.Cost) as Cost 
        from CP_Prices as p 
        join Products as pr on pr.Id = p.ProductId 
        group by pr.guid""")
        return cursor.fetchall()