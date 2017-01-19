# simpleSELECT.py
#
# simple demo of using the parsing library to do simple-minded SQL parsing
# could be extended to include where clauses etc.
#
# Copyright (c) 2003,2016, Paul McGuire
#
# Modified by Junhui Hu<junhui188@aliyun.com>

from pyparsing import Literal, CaselessLiteral, Word, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword, upcaseTokens

# define simple search
searchStmt = Forward()
# define SQL tokens
selectStmt = Forward()
SELECT = Keyword("select", caseless=True)
FROM = Keyword("from", caseless=True)
WHERE = Keyword("where", caseless=True)
GROUP_BY = Keyword("group by", caseless=True)
ORDER_BY = Keyword("order by", caseless=True)
HAVING = Keyword("having", caseless=True)
LIMIT = Keyword("limit", caseless=True)
OFFSET = Keyword("offset", caseless=True)

ident          = Word( alphas, alphanums + "_$" ).setName("identifier")
# Remove upcaseTokens
#columnName     = ( delimitedList( ident, ".", combine=True ) ).setName("column name").addParseAction(upcaseTokens)
columnName     = ( delimitedList( ident, ".", combine=True ) ).setName("column name")
columnNameList = Group( delimitedList( columnName ) )
#tableName      = ( delimitedList( ident, ".", combine=True ) ).setName("table name").addParseAction(upcaseTokens)
tableName      = ( delimitedList( ident, ".", combine=True ) ).setName("table name")
tableNameList  = Group( delimitedList( tableName ) )

whereExpression = Forward()
and_ = Keyword("and", caseless=True)
or_ = Keyword("or", caseless=True)
in_ = Keyword("in", caseless=True)
# Add not in support
not_in_ = Keyword("not in", caseless=True)

# Add is and is not support
is_ = Keyword("is", caseless=True)
is_not_ = Keyword("is not", caseless=True)

E = CaselessLiteral("E")
# Add like and regexp support
binop = oneOf("= != < > >= <= eq ne lt le gt ge like regexp", caseless=True)
arithSign = Word("+-",exact=1)
realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
                                          ( "." + Word(nums) ) ) +
                  Optional( E + Optional(arithSign) + Word(nums) ) )
intNum = Combine( Optional(arithSign) + Word( nums ) +
                 Optional( E + Optional("+") + Word(nums) ) )

asc_desc = oneOf("asc desc", caseless=True)

ordercolumn = columnName + Optional(asc_desc)

ordercolumnList = delimitedList(Group(ordercolumn))

columnRval = realNum | intNum | quotedString | columnName # need to add support for alg expressions
whereCondition = Group(
                       ( columnName + binop + columnRval ) |
                       ( columnName + in_ + "(" + delimitedList( columnRval ) + ")" ) |
                       ( columnName + in_ + "(" + selectStmt + ")" ) |
                       ( columnName + not_in_ + "(" + delimitedList( columnRval ) + ")" ) |
                       ( columnName + not_in_ + "(" + selectStmt + ")" ) |
                       ( columnName + is_not_ + columnRval) |
                       ( columnName + is_ + columnRval) |
                       ( "(" + whereExpression + ")" )
                       )
whereExpression << whereCondition + ZeroOrMore( ( and_ | or_ ) + whereExpression )

# define the grammar
selectStmt <<= (SELECT + ('*' | columnNameList)("columns") +
                FROM + tableNameList( "tables" ) +
                Optional(Group(WHERE + whereExpression), "")("where") +
                Optional(GROUP_BY + columnNameList)("group_by") +
                Optional(HAVING + whereExpression)("having") +
                Optional(ORDER_BY + ordercolumnList)("order_by") +
                Optional(LIMIT + intNum)("limit") +
                Optional(OFFSET + intNum)("offset"))

searchStmt <<= (Group(whereExpression)("where") +
                Optional(GROUP_BY + columnNameList)("group_by") +
                Optional(HAVING + whereExpression)("having") +
                Optional(ORDER_BY + ordercolumnList)("order_by"))

simpleSELECT = selectStmt

simpleSEARCH = searchStmt

# define Oracle comment format, and ignore them
oracleSqlComment = "--" + restOfLine
simpleSELECT.ignore( oracleSqlComment )

if __name__ == "__main__":
    simpleSELECT.runTests("""\
        
        # multiple tables
        SELECT * from XYZZY, ABC
        
        # dotted table name
        select * from SYS.XYZZY
        
        Select A from Sys.dual
        
        Select A,B,C from Sys.dual
        
        Select A, B, C from Sys.dual, Table2
        
        # FAIL - invalid SELECT keyword
        Xelect A, B, C from Sys.dual
        
        # FAIL - invalid FROM keyword
        Select A, B, C frox Sys.dual
        
        # FAIL - incomplete statement
        Select
        
        # FAIL - incomplete statement
        Select * from
        
        # FAIL - invalid column
        Select &&& frox Sys.dual
        
        # where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE')
        
        # compound where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE') and b in (10,20,30)
        
        # where clause with comparison operator
        Select A,b from table1, table2 where table1.id  eq  table2.id and table1.name=2 or table1.TExt    != 3 and b not in (1, 2) and c like '%abc%' group by zz limit 1 offset 3""")
