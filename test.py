import xxtea
import utils

def encrypt():
    inFp = open('compile_lua_record.json', 'rb')
    buff = inFp.read()
    inFp.close()

    buff = xxtea.encrypt(buff)

    outFp = open('a.json', 'wb')
    outFp.write(buff)
    outFp.close()

def decrypt():
    inFp = open('a.json', 'rb')
    buff = inFp.read()
    inFp.close()

    buff = xxtea.decrypt(buff)

    outFp = open('b.json', 'wb')
    outFp.write(buff)
    outFp.close()

def xxteaTest():
    encrypt()
    decrypt()

def utilsTest():
    record = {}
    record['name'] = 'zhx'
    record['num'] = '123'

    utils.generateRecord('record.jccx', record)

    record = utils.loadRecord('record.jccx')
    print('name=%s, num=%s' % (record['name'], record['num']))

if __name__ == '__main__':
    # xxteaTest()
    utilsTest()
   

    