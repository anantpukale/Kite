# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from matplotlib import pyplot


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #print_hi('PyCharm')
    from sklearn.metrics import mean_absolute_error
    # check prophet version
    # import fbprophet
    #
    # # print version number
    # print('Prophet %s' % fbprophet.__version__)
    # from pandas import read_csv
    #
    # # load data
    # path = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv'
    # df = read_csv(path, header=0)
    # # summarize shape
    # print(df.shape)
    # # show first few rows
    # print(df.head())
    #
    # from pandas import read_csv
    # from matplotlib import pyplot
    #
    # # load data
    # path = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv'
    # df = read_csv(path, header=0)
    # # plot the time series
    # df.plot()
    # # pyplot.show()
    #
    # ...
    # # prepare expected column names
    # from pandas import to_datetime
    # df.columns = ['ds', 'y']
    # df['ds'] = to_datetime(df['ds'])

    # fit prophet model on the car sales dataset
    from pandas import read_csv, to_datetime

    from fbprophet import Prophet

    # load data
    path = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv'
    df = read_csv(path, header=0)
    # prepare expected column names
    df.columns = ['ds', 'y']
    df['ds'] = to_datetime(df['ds'])
    # define the model
    model = Prophet()
    # fit the model
    model.fit(df)

    # define the period for which we want a prediction
    from pandas import DataFrame
    future = list()
    for i in range(1, 13):
        date = '1969-%02d' % i
        future.append([date])
    future = DataFrame(future)
    future.columns = ['ds']
    future['ds'] = to_datetime(future['ds'])

    ...
    forecast = model.predict(future)
    # summarize the forecast
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head())
    model.plot(forecast)
    pyplot.show()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
