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

    def set_products(self, products):
        # Check and set Partners
        cursor = self.connection.cursor()
        GUIDS = list(set([_['GUID'] for _ in products]))
        placeholders = ", ".join(["?"] * len(GUIDS))
        cursor.execute("""select pa.Guid, pa.Id, w.Id as wId, w.Name, c.ShortName from Partners as pa
                        left join CP_PaW as cpw on pa.Id = cpw.PartnerId
                        left join CP_Workers as w on cpw.WorkerId = w.Id
                        left join Cities as c on cpw.City = c.Id
                        where pa.Guid in ("""+placeholders+")", GUIDS)
        tab1 = cursor.fetchall()
        dict1 = {key[0].strip(): tab1[i] for i, key in enumerate(tab1)}
        if len(tab1) != len(GUIDS):
            GUIDS_res = [_[0] for _ in tab1]
            newGUIDS = list(set(GUIDS).difference(GUIDS_res))
            placeholders = ", ".join(["(?, 0)"] * len(newGUIDS))
            cursor.execute("""insert into Partners (Guid, Unused) values """+placeholders, newGUIDS)
            cursor.commit()
            placeholders = ", ".join(["?"] * len(newGUIDS))
            cursor.execute("""select pa.Guid, pa.Id, None, None from Partners as pa
                            where pa.Guid in ("""+placeholders+")", newGUIDS)
            tab1_1 = cursor.fetchall()
            dict1 = {**dict1, **{key[0].strip(): tab1_1[i] for i, key in enumerate(tab1_1)}}

        GUIDS = list(set([_['GUID'] for __ in products for _ in __['products']]))
        placeholders = ", ".join(["?"] * len(GUIDS))
        cursor.execute("""select p.Guid, p.Id from Products as p
                        where p.Guid in ("""+placeholders+")", GUIDS)
        tab2 = cursor.fetchall()
        dict2 = {key[0].strip(): tab2[i] for i, key in enumerate(tab2)}
        if len(tab2) != len(GUIDS):
            GUIDS_res = [_[0] for _ in tab2]
            newGUIDS = list(set(GUIDS).difference(GUIDS_res))
            placeholders = ", ".join(["(?, 0)"] * len(newGUIDS))
            cursor.execute("""insert into Products (Guid, Unused) values """+placeholders, newGUIDS)
            cursor.commit()
            placeholders = ", ".join(["?"] * len(newGUIDS))
            cursor.execute("""select p.Guid, p.Id from Products as p
                            where p.Guid in ("""+placeholders+")", newGUIDS)
            tab2_1 = cursor.fetchall()
            dict2 = {**dict2, **{key[0].strip(): tab2_1[i] for i, key in enumerate(tab2_1)}}

        ID = []
        for partner in products:
            for product in partner['products']:
                ID.append(str(dict1[partner['GUID']][1])+':'+str(dict2[product['GUID']][1]))
        placeholders = ", ".join(["?"] * len(ID))
        cursor.execute("""select cp.PartnerId, cp.ProductId, cp.URL from CP_Prices as cp 
                        where CAST(cp.PartnerId as varchar(20))+':'+ CAST(cp.ProductId as varchar(20)) in ( """+placeholders+")", ID)
        tab3 = cursor.fetchall()

        newID = []
        dict3 = {}
        newID_groupsize = 3
        def addnewID(paID, prID, product, dct):
            dct = {'URL': product['URL']}
            newID.append(paID)
            newID.append(prID)
            newID.append(product['URL'])

        for row in tab3:
            if row[0] not in dict3:
                dict3[row[0]] = {}
            dict3[row[0]][row[1]] = {'URL': row[2]}

        for partner in products:
            for product in partner['products']:
                paID = dict1[partner['GUID']][1]
                prID = dict2[product['GUID']][1]

                if paID not in dict3:
                    dict3[paID] = {}
                    addnewID(paID, prID, product, dict3[paID][prID])
                    continue
                if prID not in dict3[paID]:
                    addnewID(paID, prID, product, dict3[paID][prID])
                    continue

                if dict3[paID][prID]['URL'] == product['URL']:
                    del dict3[paID][prID]
                    if len(dict3[paID]) == 0:
                        del dict3[paID]
                else:
                    addnewID(paID, prID, product, dict3[paID][prID])

        if len(newID) > 0:
            placeholders = ", ".join(["(" + ", ".join(["?"] * newID_groupsize) +")"] * (len(newID) // newID_groupsize))
            cursor.execute("""
                            merge CP_Prices as target
                            using (select * from (
                                values """+placeholders+"""
                                ) as s (PartnerId, ProductId, URL)
                                ) as source
                            on target.PartnerId = source.PartnerId and target.ProductId = source.ProductId
                            when matched then
                                update set URL = source.URL, Parameter = NULL, LastUpdate = NULL, LastRequest = NULL
                            when not matched then
                                insert (PartnerId, ProductId, URL) values (
                                source.PartnerId, 
                                source.ProductId, 
                                source.URL);
                            
                            SELECT * from CP_Prices""", newID)
            cursor.commit()


        return {dict1[key][1]: dict1[key] for key in dict1}, {dict2[key][1]: dict2[key] for key in dict2}, dict3


    def get_partnersID_by_worker_request(self, wName, cities):
        placeholders = ", ".join(["?"] * len(cities))
        cursor = self.connection.cursor()
        cursor.execute("""select pa.Id, c.ShortName from Partners as pa
                        left join CP_PaW as cpw on pa.Id = cpw.PartnerId
                        left join CP_Workers as w on cpw.WorkerId = w.Id
                        left join Cities as c on cpw.City = c.Id
                        where w.Name=? and c.ShortName in (""" + placeholders +")", [wName, *cities])
        tab1 = cursor.fetchall()
        dict1 = {}
        for row in tab1:
            dict1[row[1].strip()] = row[0]
        return dict1


    def set_param(self, products, paID):
        products_groupsize = 2
        placeholders = ", ".join(["(" + ", ".join(["?"] * products_groupsize) +")"] * (len(products)))
        param = []
        for product in products:
            param.append(product['id'])
            param.append(product['param'])
        param.append(paID)
        cursor = self.connection.cursor()
        cursor.execute("""merge CP_Prices as target
                        using (select * from (
                            values """ + placeholders + """
                            ) as s (ProductId, Parameter)
                            ) as source
                        on target.PartnerId = ? and target.ProductId = source.ProductId
                        when matched then
                            update set Parameter = source.Parameter;""", param)
        cursor.commit()

    def set_prices(self, products, paID):
        products_groupsize = 2
        placeholders = ", ".join(["(" + ", ".join(["?"] * products_groupsize) +")"] * (len(products)))
        param = []
        for product in products:
            param.append(product['id'])
            param.append(product['price'])
        param.append(paID)
        param.append(paID)
        cursor = self.connection.cursor()
        cursor.execute("""merge CP_Prices as target
                        using (select * from (
                            values """ + placeholders + """
                            ) as s (ProductId, Cost)
                            ) as source
                        on target.PartnerId = ? and target.ProductId = source.ProductId
                        when matched then
                            update set Cost = source.Cost, LastUpdate = getdate()
                        when not matched then
                            insert(PartnerId, ProductId, Cost, LastUpdate) values (
                            ?, source.ProductId, source.Cost, getdate());""", param)
        cursor.commit()


    def get_products(self, wName):
        cursor = self.connection.cursor()
        cursor.execute("""select c.ShortName, cpp.ProductId, cpp.URL, cpp.Parameter from CP_Workers as w
                        left join CP_PaW as cpw on w.Id = cpw.WorkerId
                        left join Cities as c on cpw.City = c.Id
                        left join CP_Prices as cpp on cpw.PartnerId = cpp.PartnerId
                        where w.Name = ? and cpp.URL is not null;""", (wName,))
        tab1 = cursor.fetchall()
        return tab1

    def get_workers_name(self):
        cursor = self.connection.cursor()
        cursor.execute("""select w.Name from CP_Workers as w""")
        tab1 = cursor.fetchall()
        return [row[0].strip() for row in tab1]

