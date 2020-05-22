# import pandas as pd

# from unittest.mock import Mock

# from pdlog.accessor import LogAccessor


# def test_accessor_add_hooks(monkeypatch):
#     before_df = Mock()
#     after_df = Mock()
#     before_df.logged_method = Mock(return_value=after_df)
#     after_hook = Mock()

#     # Also need to mock the method on pd.DataFrame, since the patched method calls
#     # functools.wrap on the original pd.DataFrame method.
#     pd.DataFrame.logged_method = Mock()

#     # Patch the accessor class' logged_method
#     accessor_cls = LogAccessor
#     accessor_cls.logged_method = accessor_cls.add_hooks("logged_method", after_hook)

#     # Instantiate an accessor and call the patched method
#     accessor = LogAccessor(before_df)
#     args = (0, 1, 2)
#     kwargs = dict(key0=0, key1=1, key2=2)
#     accessor.logged_method(*args, **kwargs)

#     # patched method calls the underlying logged_method with args and kwargs.
#     before_df.logged_method.assert_called_with(*args, **kwargs)
#     # patched method calls after_hook with before_df and the result of logged_method.
#     after_hook.assert_called_with(before_df, after_df, "logged_method")
