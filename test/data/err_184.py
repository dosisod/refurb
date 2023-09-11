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


# these will not
def no_match():
    y = 10
    y = transform(y)
    return y
