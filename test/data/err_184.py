class torch:
    @staticmethod
    def ones(*args):
        return torch

    @staticmethod
    def long():
        return torch

    @staticmethod
    def to(device: str):
        return torch.Tensor()

    class Tensor:
        pass


def transform(x):
    return x


class spark:
    class read:
        @staticmethod
        def parquet(file_name: str):
            return spark.DataFrame()

    class functions:
        @staticmethod
        def lit(constant):
            return constant

        @staticmethod
        def col(col_name):
            return col_name

    class DataFrame:
        @staticmethod
        def withColumnRenamed(col_in, col_out):
            return spark.DataFrame()

        @staticmethod
        def withColumn(col_in, col_out):
            return spark.DataFrame()

        @staticmethod
        def select(*args):
            return spark.DataFrame()

class F:
    @staticmethod
    def lit(value):
        return value


# these will match
def get_tensors(device: str) -> torch.Tensor:
    a = torch.ones(2, 1)
    a = a.long()
    a = a.to(device)
    return a


def process(file_name: str):
    common_columns = ["col1_renamed", "col2_renamed", "custom_col"]
    df = spark.read.parquet(file_name)
    df = df \
        .withColumnRenamed('col1', 'col1_renamed') \
        .withColumnRenamed('col2', 'col2_renamed')
    df = df \
        .select(common_columns) \
        .withColumn('service_type', spark.functions.lit('green'))
    return df


def projection(df_in: spark.DataFrame) -> spark.DataFrame:
    df = (
        df_in.select(["col1", "col2"])
        .withColumnRenamed("col1", "col1a")
    )
    return df.withColumn("col2a", spark.functions.col("col2").cast("date"))


def assign_multiple(df):
    df = df.select("column")
    result_df = df.select("another_column")
    final_df = result_df.withColumn("column2", F.lit("abc"))
    return final_df


# not yet supported
def assign_alternating(df, df2):
    df = df.select("column")
    df2 = df2.select("another_column")
    df = df.withColumn("column2", F.lit("abc"))
    return df, df2


# these will not
def ignored(x):
    _ = x.op1()
    _ = _.op2()
    return _

def _(x):
    y = x.m()
    return y.operation(*[v for v in y])


def assign_multiple_referenced(df, df2):
    df = df.select("column")
    result_df = df.select("another_column")
    return df, result_df


def invalid(df_in: spark.DataFrame, alternative_df: spark.DataFrame) -> spark.DataFrame:
    df = (
        df_in.select(["col1", "col2"])
        .withColumnRenamed("col1", "col1a")
    )
    return alternative_df.withColumn("col2a", spark.functions.col("col2").cast("date"))


def no_match():
    y = 10
    y = transform(y)
    return y

def f(x):
    if x:
        name = "alice"
        stripped = name.strip()
        print(stripped)
    else:
        name = "bob"
    print(name)

def g(x):
    try:
        name = "alice"
        stripped = name.strip()
        print(stripped)
    except ValueError:
        name = "bob"
    print(name)

def h(x):
    for _ in (1, 2, 3):
        name = "alice"
        stripped = name.strip()
        print(stripped)
    else:
        name = "bob"
    print(name)

def assign_multiple_try(df):
    try:
        df = df.select("column")
        result_df = df.select("another_column")
        final_df = result_df.withColumn("column2", F.lit("abc"))
        return final_df
    except ValueError:
        return None
