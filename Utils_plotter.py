import finplot as fplt
from matplotlib import pyplot as plt
# imports
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from LogRoot.Logging import Logger
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix, average_precision_score, precision_recall_curve


def plot_candle_patter(df):
    #https://stackoverflow.com/questions/9673988/intraday-candlestick-charts-using-matplotlib
    ax = fplt.create_plot("symbol")


    fplt.candlestick_ochl(df[['Open', 'Close', 'High', 'Low']], ax=ax)
    fplt.plot(df['Close'].rolling(200).mean(), ax=ax, legend='SMA 200')
    fplt.plot(df['Close'].rolling(50).mean(), ax=ax, legend='SMA 50')
    fplt.plot(df['Close'].rolling(20).mean(), ax=ax, legend='SMA 20')

    #df.set_index('Date', inplace=True)
    fplt.volume_ocv(df[['Open', 'Close', 'Volume']] , ax=ax.overlay() )

    fplt.show()

def plotting_financial_chart_buy_points_serial(df, buy_points_serial = None, stockId = "",opion_time_name = ""):
    fig = go.Figure(go.Candlestick(x=df.index,
                                   open=df['Open'],
                                   high=df['High'],
                                   low=df['Low'],
                                   close=df['Close']))

    # removing rangeslider
    fig.update_layout(xaxis_rangeslider_visible=False)
    # hide weekends
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    # removing all empty dates
    # build complete timeline from start date to end date
#dt_all = pd.date_range(start=df['Date'][0], end=df['Date'][len(df['Date'])-1])
    dt_all = pd.date_range(start=df.index[0], end=df.index[-1])
    # retrieve the dates that ARE in the original datset
    dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df.index)]
    # define dates with missing values
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    #Print MA s
    # fig.add_trace(go.Scatter(x=df.index,
    #                          y=df['MA5'],
    #                          opacity=0.7,
    #                          line=dict(color='blue', width=2),
    #                          name='MA 5'))
    # fig.add_trace(go.Scatter(x=df.index,
    #                          y=df['MA20'],
    #                          opacity=0.7,
    #                          line=dict(color='orange', width=2),
    #                          name='MA 20'))

    if buy_points_serial is not  None:
        medium_price = df['Close'].mean()
        buy_points_serial =  (buy_points_serial/100).astype(int)
        buy_points_serial = int(medium_price/10) * buy_points_serial
        buy_points_serial = buy_points_serial + medium_price
        fig.add_trace(go.Scatter(x=df.index,
                                 y=buy_points_serial,
                                 opacity=0.7,
                                 line=dict(color='blue', width=1.2),
                                 name='Buy points'))


    # hide dates with no values
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])
    # remove rangeslider
    fig.update_layout(xaxis_rangeslider_visible=False)
    # add chart title
    fig.update_layout(title=stockId +"_"+opion_time_name)


    # html file print
    #fig.write_image("d_price/" + stockId + "_stock_history_BUY_points_"+opion_time_name+".png")
    #fig.write_image("d_price/" + stockId + "_stock_history_BUY_points_" + opion_time_name + ".pdf")
    plotly.offline.plot(fig, show_link=True,auto_open=True, filename="d_price/" + stockId + "_stock_history_BUY_points_"+opion_time_name+".html")
    Logger.logr.info("d_price/" + stockId + "_stock_history_BUY_points_"+opion_time_name+".html  stock: " + stockId + " Shape: " + str(df.shape))

    fig.show()

def __autopct_fun(abs_values):
    #Source: https://www.holadevs.com/pregunta/64169/adding-absolute-values-to-the-labels-of-each-portion-of-matplotlibpyplotpie
    gen = iter(abs_values)
    return lambda pct: f"{pct:.1f}% ({next(gen)})"

def plot_pie_countvalues(df, colum_count , stockid= "", opion = "", path=None ):
    df =  df.groupby(colum_count).count()
    y = np.array(df['Date'])

    plt.figure()
    plt.pie( y , labels=df.index, autopct=__autopct_fun(y),startangle=9, shadow=True)

    name = "plot_pie_"+stockid + "_"+colum_count+"_"+opion
    plt.title("Count times values:\n"+ name)
    if path is not None:
        plt.savefig(path +name + ".png")
        Logger.logr.info(path +name + ".png  stock: " + stockid)


def plolt_show_correlations(dataframe, fontSize):
    fig = plt.figure(figsize=(20, 10))
    corr = dataframe.corr()
    # para solo mostar 2 decimales
    # make_float = lambda x: "${:,.2f}".format(x)
    # corr.apply(make_float)

    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        ax = sns.heatmap(corr, mask=mask, vmax=.3, annot=True, cmap="YlGnBu", annot_kws={"size": fontSize},
                         linewidths=.5, square=True)
    # if show_chart == True:
    #   sns.heatmap(corr,
    #              xticklabels=corr.columns.values,
    #              yticklabels=corr.columns.values,
    #             annot=True, cmap="YlGnBu", annot_kws={"size": 18}, linewidths=.5, square=True)
    plt.savefig("d_price/show_correlations.png")
    print("d_price/show_correlations.png")
    return corr

import itertools
def plot_confusion_matrix(cm, classes,y_test,# TODO entender si puede ser opcional y_test
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues,
                          pathImg = None
                          ):
    """
    Esta función imprime y grafica la matriz de confusión.
    La normalización se puede aplicar configurando `normalize=True`.
    """
    plt.figure()
    label_test = y_test

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        ##int("Matriz de confusión normalizada")
    #lse:
        #pint('Matriz de confusión, sin normalización')
    #rint(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title, fontsize=18)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('Etiqueta verdadera')
    plt.xlabel('Previsión Correcta')

    if pathImg is not None:
        plt.savefig(pathImg)
        print("generate "+ pathImg)

def plot_confusion_matrix_cm_IN(y_test, predictions,path = None, p=0.5):
    cm = confusion_matrix(y_test, predictions > p)
    plot_confusion_matrix_cm_OUT(cm, path, title_str ='Confusion matrix @{:.2f}'.format(p))

    tn, fp, fn, tp = cm.ravel()

    recall = tp / (tp + fn)
    precision = tp / (tp + fp)
    F1 = 2*recall*precision/(recall+precision)

    print('Recall={0:0.3f}'.format(recall),'\nPrecision={0:0.3f}'.format(precision))
    print('F1={0:0.3f}'.format(F1))


    print('Legitimate Transactions Detected (True Negatives): ', cm[0][0])
    print('Legitimate Transactions Incorrectly Detected (False Positives): ', cm[0][1])
    print('Fraudulent Transactions Missed (False Negatives): ', cm[1][0])
    print('Fraudulent Transactions Detected (True Positives): ', cm[1][1])
    print('Total Fraudulent Transactions: ', np.sum(cm[1]))

def plot_bars_feature_importances(columns_bars,num_volu_bars, num_bars = 20, path_bars = None):
    feature_df = pd.DataFrame()
    feature_df['features'] = columns_bars
    feature_df['importance'] = num_volu_bars
    feature_df = feature_df.sort_values(by='importance', ascending=False)
    # print('Variables más Referentes')
    feature_df = feature_df.set_index(keys='features').sort_values(by='importance', ascending=False)
    # feature_df.set_index(keys='features').sort_values(by='importance', ascending=True).plot(
    #     label='Variables más Referentes', kind='barh', figsize=(20, 15))
    # feature_df.plot(kind='barh')
    # feature_df.set_index(keys='features').sort_values(by='importance', ascending=True).plot.bar(stacked=True)
    # plot stacked bar chart
    plt.figure() #clean sub plots
    # plt.figure().clear()
    # plt.cla()
    # plt.clf()
    # plt.close()
    y_pos = np.arange(len(feature_df.index[:num_bars]))
    plt.barh(y_pos, feature_df['importance'][:num_bars], align='center', alpha=0.5)
    plt.yticks(y_pos, feature_df.index[:num_bars])
    plt.xlabel('Columns')
    plt.title('Variables más Referentes')
    if path_bars is not None:
        plt.savefig(path_bars)
        feature_df.to_csv(path_bars+".csv")
        print("generate " + path_bars)


def plot_feature_importances_loans(model, X, path = None ):
    try:
        loans_features = [x for i, x in enumerate(X.columns) if i != len(X.columns)]
        plt.figure(figsize=(160,90))
        n_features = len(X.columns)
        plt.barh(range(n_features), model.feature_importances_, align='center')
        plt.yticks(np.arange(n_features), loans_features)
        plt.xlabel("Feature importance")
        plt.ylabel("Feature")
        plt.ylim(-1, n_features)

        if path is not None:
            print("plot_feature_importances_loans  "+ path)
            plt.savefig(path)
    except Exception as e:
        # Logger.logr.warning(e)
        print("Exception: "+ str(e))


#https://www.stackvidhya.com/plot-confusion-matrix-in-python-and-why/
def plot_confusion_matrix_cm_OUT(cf_matrix, path = None, title_str ='Seaborn Confusion Matrix with labels\n\n'):
    plt.figure()

    labels = ['True Neg','False Pos','False Neg','True Pos']
    labels = np.asarray(labels).reshape(2,2)

    cm_sum = np.sum(cf_matrix, axis=1, keepdims=True)
    cm_perc = cf_matrix / cm_sum.astype(float) * 100
    annot = np.empty_like(cf_matrix).astype(str)
    nrows, ncols = cf_matrix.shape
    for i in range(nrows):
        for j in range(ncols):
            c = cf_matrix[i, j]
            p = cm_perc[i, j]
            if i == j:
                s = cm_sum[i]
                annot[i, j] = '%.1f%%\n%d/%d' % (p, c, s)
            elif c == 0:
                annot[i, j] = ''
            else:
                annot[i, j] = '%.1f%%\n%d' % (p, c)
    cm = pd.DataFrame(cf_matrix, index=labels, columns=labels)
    cm.index.name = 'Actual'
    cm.columns.name = 'Predicted'

    #ax = sns.heatmap(cf_matrix, annot=labels, fmt='', cmap='Blues')
    # ax = sns.heatmap(cf_matrix / np.sum(cf_matrix), annot=True,
    #                  fmt='.2%', cmap='Blues')
    print("annot NEGATIVES: ", annot[0]," POSITIVEs: ", annot[1])
    ax =  sns.heatmap(cm, annot=annot, fmt='', cmap='Blues')

    ax.set_title(title_str);
    ax.set_xlabel('\nPredicted Values')
    ax.set_ylabel('Actual Values ');

    ## Ticket labels - List must be in alphabetical order
    ax.xaxis.set_ticklabels(['False','True'])
    ax.yaxis.set_ticklabels(['False','True'])


    ## Display the visualization of the Confusion Matrix.
    # plt.show()
    if path is not None:
        print("plot_confusion_matrix  " + path)
        plt.savefig(path)

def plot_cm_TF_imbalance(labels, predictions,path = None, p=0.5):
  cm = confusion_matrix(labels, predictions > p)
  plot_confusion_matrix_cm_OUT(cm, path = path, title_str ='Confusion matrix @{:.2f}'.format(p))
  print('Legitimate Transactions Detected (True Negatives): ', cm[0][0])
  print('Legitimate Transactions Incorrectly Detected (False Positives): ', cm[0][1])
  print('Fraudulent Transactions Missed (False Negatives): ', cm[1][0])
  print('Fraudulent Transactions Detected (True Positives): ', cm[1][1])
  print('Total Fraudulent Transactions: ', np.sum(cm[1]))


def plot_relationdist_main_val_and_all_rest_val(df, main_name = 'buy_sell_point', path = "plots_relations\plot_relationdistplot_"):
    # plt.figure(figsize=(12,IMAGES_PER_PNG_FILE*4))
    import matplotlib.gridspec as gridspec
    features = df.iloc[:].columns
    gs = gridspec.GridSpec(30, 1)
    for i, ele_B in enumerate(df[features]):
        plt.figure()
        if (ele_B.startswith('cdl_') or ele_B.startswith('mcrh_') or  ele_B.startswith('pcrh_')or  ele_B.startswith('has_') or ('_crash' in ele_B) ):

            x, y =  ele_B , main_name

            df1 = df.groupby(x)[y].value_counts(normalize=True)
            df1 = df1.mul(100)
            df1 = df1.rename('percent').reset_index()

            g = sns.catplot(x=x, y='percent', hue=y, kind='bar', data=df1)
            g.ax.set_ylim(0, 100)

            for p in g.ax.patches:
                txt = str(p.get_height().round(2)) + '%'
                txt_x = p.get_x()
                txt_y = p.get_height()
                g.ax.text(txt_x, txt_y, txt)
        else:
            # condition_filter_b = (df[ele_B] == df[ele_B])#se recoge la condicion para incluir a todos
            # if ele_B.startswith("cdl_"):
            #     #Es un padron de vela se trata distinto, para que se vea bonito
            #     max_b = 100
            #     min_b = -100
            #     condition_filter_b = (df[ele_B] == max_b) | (df[ele_B] == min_b)
            sns.distplot(df[ele_B][(df[main_name] == 1)], bins=50)
            sns.distplot(df[ele_B][(df[main_name] == 0)], bins=50)
            # plt.set_xlabel('')
            # plt.set_title('Feature: ' + str(ELEMENT_B))
        plt.title("Count relation values:\n" + main_name + "__" + ele_B)
        if path is not None:
            print(path + main_name + "__" + ele_B + ".png")
            plt.savefig(path + main_name + "__" + ele_B + ".png")



def plot_average_precision_score(y_test, scores,path = None):
    plt.figure()
    precision, recall, _ = precision_recall_curve(y_test, scores, pos_label=0)
    average_precision = average_precision_score(y_test, scores)

    print('Average precision-recall score: {0:0.3f}'.format(
          average_precision))

    plt.plot(recall, precision, label='area = %0.3f' % average_precision, color="green")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision Recall Curve')
    plt.legend(loc="best")
    if path is not None:
        print("plot Average precision-recall  " + path)
        plt.savefig(path)

#TODO https://colab.research.google.com/drive/1940aC6X6xyeJNTP1qnfxoHhQZwGa_yOx#scrollTo=T0UYEnkwm8Fe
def plot_candle_beatufull_proportion_values():
    df_std = (df - train_mean) / train_std
    df_std = df_std.melt(var_name='Column', value_name='Normalized')

    plt.figure(figsize=(25 * len(df_std.columns), 13 * len(df_std.columns)))
    ax = sns.violinplot(x='Column', y='Normalized', data=df_std)
    _ = ax.set_xticklabels(df.keys(), rotation=90)

    plt.title("Count times values:\n")
    plt.savefig("violinplot_.png")
# One advantage to linear Models is that they're relatively simple to interpret. You can pull out the layer's weights and visualize the weight assigned to each input:
def plot_weights_and_visualize():
    plt.figure(figsize=(25 * len(df_std.columns), 13 * len(df_std.columns)))

    plt.bar(x=range(len(train_df.columns)),
            height=linear.layers[0].kernel[:, 0].numpy())
    axis = plt.gca()
    axis.set_xticks(range(len(train_df.columns)))
    _ = axis.set_xticklabels(train_df.columns, rotation=90)

    plt.title("Count times values:\n")
    plt.savefig("weights and visualize.png")