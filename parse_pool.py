from grab import Grab
import json
from time import sleep

from suprnova import SuprnovaParse, record_subdom, read_file_supr

POOLS = ['hashrefinery', 'nanopool_eth', 'lbrypool', 'nanopool_zec', 'nanopool_etc']
LOGS = [r'Resource\hashrefinery_log.txt', 
        u'Resource\\nanopool_eth_log.txt', 
        u'Resource\\lbrypool_log.txt',
        u'Resource\\nanopool_zec_log.txt',
        u'Resource\\nanopool_etc_log.txt']

class parsePool():
    g = Grab()    
    name = ''
    def __init__(self, _name, address, _pool ):
        self.name = _name
        if _pool == POOLS[0]:
            self.g.go('http://pool.hashrefinery.com/site/wallet_miners_results?address=' + address)
            
        elif _pool == POOLS[2]:
            self.g.go('https://lbrypool.com/site/wallet_miners_results?address=' + address)
            
        elif _pool == POOLS[1]:
            self.g.go('https://eth.nanopool.org/api/v1/workers/{address}/0/50/id_ASC_all'.format(address = address))
            
        elif _pool == POOLS[3]:
            self.g.go('https://zec.nanopool.org/api/v1/workers/{address}/0/50/id_ASC_all'.format(address = address))
            
        elif _pool == POOLS[4]:
            self.g.go('https://etc.nanopool.org/api/v1/workers/{address}/0/50/id_ASC_all'.format(address = address))


    def get_data_nanopool(self):
        dic = json.loads(self.g.doc.body.decode('utf-8'))                  #decode from str in dict
        workers = dic['data']['workers'][:]
        data = []
        for item in workers:
            tmp = []
            tmp.append(item['id'])
            tmp.append(item['hashrate'])
            data.append(tmp)   
        return data

    def write_data_nanopool(self):
        array = self.get_data_nanopool() 
        with open ('nanopool_result.log', 'a') as f:
            f.write('\n' + self.name + ':')
            [f.write('\t\t' + item[0] + '  -->  ' + item[1] + 'Mh/s\n') for item in array]
            f.write('\n---------------------------------------------------------------------------------------------')
            if not f.closed:
                f.close()
            
    
            
    '''
    def get_thead_hashrefinery(self):
        thead = ['Deatails', '\tExtra', 'Algo', '\tDiff','Hashrate']
        #[thead.append(item.text()) for item in self.g.doc.select('//table[@class="dataGrid2"][2]/thead/tr/th') if item.text() != '']
        return thead
    '''

    def get_tr_hashrefinery(self):
        tr = []
        for j in range(len( self.g.doc.select('//table[@class="dataGrid2"][2]/tr[@class = "ssrow"]'))):
            tmp = []
            [tmp.append(item.text()) for item in self.g.doc.select('//table[@class="dataGrid2"][2]/tr[@class = "ssrow"][{iter}]/td'.format(iter = j+1)) if item.text() != '']
            tr.append(tmp)
        return tr
        

    def wirte_data_hashrefinery(self):
        tr = self.get_tr_hashrefinery()
        with open('hashrefinery_result.log', 'a') as file:
            file.write('\n' + self.name + '\n')
            for item in tr:
                [file.write('\t\t' + i.strip() ) for i in item]
                file.write('\n')
            file.write('------------------------------------------------------------------------------------------------------------------------')
            if not file.closed:
                file.close()


def first_record():
    thead = ['Deatails', '\tExtra', 'Algo', '\tDiff','Hashrate']
    with open('hashrefinery_result.log', 'w') as file:
        file.write('Name\t\t')
        [file.write( item + '\t\t') for item in thead]
        file.write('------------------------------------------------------------------------------------------------------------------------') 
        file.close()

    with open ('nanopool_result.log', 'w') as f:
            f.write('\t\t' + 'Worker      Hashrate\n')
            f.write('---------------------------------------------------------------------------------------------')
            f.close() 

    with open('suprnova.log' , 'w') as f:
        f.write('Name\t\tActive worker\t\tKahsh/s\t\tDifficulty\n')
        f.write('-----------------------------------------------------------------------------\n')


def read_file(name):
    lines = []
    with open (name, 'r') as file:
        lines = file.readlines()
        if lines == []:
            return False
        if not file.closed:
            file.close()

    for i in range(len(lines)):
        lines[i] = lines[i].strip().split(' ')
        ln = len(lines[i][1])
        if lines[i][1].rfind('\n', 0, ln) != -1:
            lines[i][1] = lines[i][1][:ln-1]         
    return lines 


def main():
    first_record()
    arr_hash = []
    for log in LOGS:
        try:
            read = read_file(log)
            if read:
                arr_hash.append(read)
        except:
            continue

    for l in range(len(arr_hash)):
        for i in  arr_hash[l]:
            p =  parsePool(i[0], i[1],  POOLS[l])     
            if POOLS[l] == 'hashrefinery' or POOLS[l] == 'lbrypool':
                p.wirte_data_hashrefinery()
            else:
                p.write_data_nanopool() 

    data_supr = read_file_supr(r'Resource\suprnova.txt')
    for item in data_supr.keys():
        record_subdom(item)
        for val in data_supr[item]:
            a = SuprnovaParse(val[0],val[1], val[2], item)
            a.record_data()
            a.Logout()     


if __name__ == '__main__':
    print('Process is doing')
    try:
        main()
        print('\nProcess has finished succesfully.\nThe window is closing in 5 seconds...')
    except Exception as ex:
        print('During processing has arisen error: ' + str((ex)))
    finally:
        sleep(5)