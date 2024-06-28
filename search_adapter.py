from robocorp import log

class SearchParamsAdapter:
    """Adapter to handle search params"""
    def __init__(self, params_payload: dict):
        params_payload = params_payload or {}
        self._phrase = params_payload.get('phrase')
        self._months = params_payload.get('months')
        self._sort_by = params_payload.get('sort_by')
        self.DEFAULT_MONTH = 1
        self.DEFAULT_SORT_BY = "Relevance"
        self.DEFAULT_PHRASE = "Olympic Games"

    @property
    def months(self):
        month_ops_is_not_positive = self._months is None or self._months < 1
        if month_ops_is_not_positive:
            return self.DEFAULT_MONTH
        
        return self._months

    @property
    def sort_by(self):
        is_a_valid_sort = self._sort_by in ['Relevance', 'Newest', 'Oldest']
        return self._sort_by if is_a_valid_sort else 'Relevance'

    @property
    def phrase(self):
        is_empty_text = (self._phrase is None 
                         or self._phrase.strip() == '')
        return self._phrase if not is_empty_text else self.DEFAULT_PHRASE

    def get_dict(self):
        search_dict = {
            "phrase": self.phrase,
            "months": self.months,
            "sort_by": self.sort_by
        }

        log.info(f"SEARCH PARAMS: {search_dict}")

        return search_dict
