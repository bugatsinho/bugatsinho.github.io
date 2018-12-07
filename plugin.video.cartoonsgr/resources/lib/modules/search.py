
import control
import urllib
import sys
from init import params

class Search:

    def search(self):
        navigator.navigator().addDirectoryItem(32603, 'tvSearchnew', 'search.png', 'DefaultTVShows.png')
        try:
            from sqlite3 import dbapi2 as database
        except:
            from pysqlite2 import dbapi2 as database

        dbcon = database.connect(control.searchFile)
        dbcur = dbcon.cursor()

        try:
            dbcur.executescript("CREATE TABLE IF NOT EXISTS tvshow (ID Integer PRIMARY KEY AUTOINCREMENT, term);")
        except:
            pass

        dbcur.execute("SELECT * FROM tvshow ORDER BY ID DESC")

        lst = []

        delete_option = False
        for (id, term) in dbcur.fetchall():
            if term not in str(lst):
                delete_option = True
                navigator.navigator().addDirectoryItem(term.title(), 'tvSearchterm&name=%s' % term, 'search.png',
                                                       'DefaultTVShows.png')
                lst += [(term)]
        dbcur.close()

        if delete_option:
            navigator.navigator().addDirectoryItem(32605, 'clearCacheSearch&select=tvshow', 'tools.png',
                                                   'DefaultAddonProgram.png')

        navigator.navigator().endDirectory(False)

    def search_new(self):
        control.idle()

        t = control.lang(32010).encode('utf-8')
        k = control.keyboard('', t);
        k.doModal()
        q = k.getText() if k.isConfirmed() else None

        if (q == None or q == ''): return
        q = q.lower()
        try:
            from sqlite3 import dbapi2 as database
        except:
            from pysqlite2 import dbapi2 as database

        dbcon = database.connect(control.searchFile)
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM tvshow WHERE term = ?", (q,))
        dbcur.execute("INSERT INTO tvshow VALUES (?,?)", (None, q))
        dbcon.commit()
        dbcur.close()
        url = self.search_link + urllib.quote_plus(q)
        if int(control.getKodiVersion()) >= 18:
            self.get(url)
        else:
            url = '%s?mode=6&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            control.execute('Container.Update(%s)' % url)

    def search_term(self, q):
        control.idle()
        q = q.lower()
        try:
            from sqlite3 import dbapi2 as database
        except:
            from pysqlite2 import dbapi2 as database

        dbcon = database.connect(control.searchFile)
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM tvshow WHERE term = ?", (q,))
        dbcur.execute("INSERT INTO tvshow VALUES (?,?)", (None, q))
        dbcon.commit()
        dbcur.close()
        url = self.search_link + urllib.quote_plus(q)
        if int(control.getKodiVersion()) >= 18:
            self.get(url)
        else:
            url = '%s?mode=tvshowPage&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            control.execute('Container.Update(%s)' % url)