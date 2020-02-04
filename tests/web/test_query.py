'''
    Biothings Query Component Common Tests
'''


from helper import BiothingsTestCase


class TestQuery(BiothingsTestCase):

    def test_01(self):
        ''' KWARGS CTRL Format Json '''
        self.query(q='__all__', size='1')

    def test_02(self):
        ''' KWARGS CTRL Format Yaml '''
        res = self.request('query?q=__all__&size=1&format=yaml').text
        assert res.startswith('max_score:')

    def test_03(self):
        ''' KWARGS CTRL Format Html '''
        res = self.request('query?q=__all__&size=1&format=html').text
        assert '<html>' in res

    def test_04(self):
        ''' KWARGS CTRL Format Msgpack '''
        res = self.request('query?q=__all__&size=1&format=msgpack').content
        self.msgpack_ok(res)

    def test_11(self):
        ''' HANDLE Unmatched Quotes'''
        # Sentry
        # Issue 529121368
        # Event 922fc99638cb4987bccbfd30c914ff03
        _q = 'query?q=c("ZNF398", "U2AF...'
        self.request(_q, expect_status=400)