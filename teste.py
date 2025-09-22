import config
import pandas
def populate_datapool(self, data: Union[List[Dict[str, str]], "pandas.DataFrame"], key: Optional[str] = None, child: bool = False) -> None:
    """
    Popula o DataPool especificado com dados, aceitando lista de dicionários ou DataFrame pandas.
    :param data: Lista de dicionários (List[Dict[str, str]]) ou pandas.DataFrame.
    :param key: Nome do campo a ser usado como entry_id, opcional.
    :param child: Se True, usa o child_datapool; caso contrário, usa o parent_datapool.
    """
    pool = self.get_datapool(child)
    is_pd = False
    try:
        import pandas as pd
        is_pd = isinstance(data, pd.DataFrame)
    except ImportError:
        is_pd = False
    if is_pd:
        for _, row in data.iterrows():
            values: Dict[str, str] = row.to_dict()
            entry_id: Optional[str] = values.get(key) if key else None
            item: DataPoolEntry = DataPoolEntry(
                task_id=self.task_id, entry_id=entry_id, values=values
            )
            pool.create_entry(item)
            print(
                f"adicionado {_ + 1} item de {len(data)} no datapool {pool.label}")
        print(
            f"{len(data)} itens inseridos no {'child' if child else 'parent'} datapool.")
    elif isinstance(data, list) and all(isinstance(r, dict) for r in data):
        for row in data:
            entry_id: Optional[str] = row.get(key) if key else None
            item: DataPoolEntry = DataPoolEntry(
                task_id=self.task_id, entry_id=entry_id, values=row
            )
            pool.create_entry(item)
        print(
            f"{len(data)} itens inseridos no {'child' if child else 'parent'} datapool.")
    else:
        raise TypeError(
            "data deve ser uma lista de dicionários ou um pandas.DataFrame")

