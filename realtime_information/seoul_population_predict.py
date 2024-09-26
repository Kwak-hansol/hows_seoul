from neuralprophet import NeuralProphet, set_log_level, set_random_seed
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
import plotly.graph_objects as go

def train_and_evaluate_model(df, plot=False):
    """
    모델을 학습하고 검증 데이터 평가
    """
    # 로깅 메시지 비활성화 및 난수 시드 설정
    set_log_level("ERROR")
    set_random_seed(0)

    # NeuralProphet 모델 생성
    m = NeuralProphet(
        n_changepoints=10,
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True,
        n_lags=10,  # 과거 데이터 10일치 사용
    )

    # 한국 공휴일 이벤트 추가
    m.add_country_holidays(country_name='KR')

    # 추가 회귀 변수로 '총생활인구수' 사용
    m.add_lagged_regressor("총생활인구수")

    # 데이터셋을 훈련 및 검증 데이터로 분할
    train_size = int(0.8 * len(df))
    df_train = df[:train_size]  # 훈련 데이터 (80%)
    df_val = df[train_size:]  # 검증 데이터 (20%)

    # 모델 학습
    m.fit(df_train, validation_df=df_val)

    # 검증 데이터에 대한 예측 수행
    forecast_val = m.predict(df_val)

    # NaN 값 처리
    df_val = df_val.dropna().reset_index(drop=True)
    forecast_val = forecast_val.dropna().reset_index(drop=True)

    # 데이터 길이 일치 여부 확인 후 일치하지 않으면 짧은 쪽에 맞춤
    min_len = min(len(df_val), len(forecast_val))
    df_val = df_val[:min_len]
    forecast_val = forecast_val[:min_len]

    # 검증 데이터에 대한 모델 성능 평가
    actual_val = df_val['y'].values
    predicted_val = forecast_val['yhat1'].values  # 예측된 값의 열 이름에 따라 조정

    # 메트릭 계산
    mse_val = mean_squared_error(actual_val, predicted_val)
    mae_val = mean_absolute_error(actual_val, predicted_val)

    # 모델 성능 출력
    print(f"검증 데이터에 대한 평균 제곱 오차 (MSE): {mse_val:.2f}")
    print(f"검증 데이터에 대한 평균 절대 오차 (MAE): {mae_val:.2f}")

    # 전체 데이터에 대해 예측 수행 (최종 예측)
    forecast_all = m.predict(df)

    # 시각화 옵션이 활성화된 경우 그래프 객체 반환
    plot_fig = None
    if plot:
        m.set_plotting_backend("plotly")
        plot_fig = m.plot(forecast_all)

    return forecast_all, mse_val, mae_val, plot_fig