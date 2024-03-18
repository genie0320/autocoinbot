# loggong

문과 + 기획자 출신인 내게... 로깅이란 언제나... 지나치게 개발개발한, 그래서 나는 print로도 충분할 것 같은 그런 존재들이었다. 하지만.. 이번에 오토코인봇을 만들면서 매일매일 타겟코인이 어떻게 달라지는지를, 문득 들어가서도 확인해볼 수 있도록 어딘가 저장을 해보고 싶었다.

crontab의 기능을 이용해도, print된 내용들을 특정 파일에 저장해볼 수 있지만, 기왕에 하는거... 뽀대나게 변경해보고 싶었다. 

간단하지만 간단하지 않았던 것이... 로깅으로 검색을 하면, 설정에 대한 이야기는 매우 많이 나오는데, 정작 그걸 어떻게 사용해야 하는지에 대해서는 나오지 않는다. 

즉... 그 config를 root의 main()에서만 해주면 되는 것인지, 그걸 불러다 쓰는 하위 파일들에서도 다 해줘야 하는 것인지... 

그간의 짬바를 활용해보자면, python은 스크립트언어 즉 자바스크립트와 같다. 결국 인터프리터가 해석을 끝내면, 하나의 거대한 실행파일이 만들어지는 구조이다. 따라서... log config는 최초로 실행되는 파일에서 한번만 해주면, 아래쪽의 모든 파일에 적용되어야 맞는 것인데... 그게 딱히 그런 것 같지도...(root > main()에서만 실행해주는데, 하위 파일에서의 logging 들은 나타나는 꼬라지를 아직 못 봤다.)

```python
# 설정
import logging

logging.basicConfig(
    level=logging.DEBUG, 
    # format = '%(asctime)s %(levelname)s %(message)s',
    format = "[%(filename)1s %(funcName)s() ] %(message)s",
    datefmt= '%Y-%m-%d %H:%M:%S',
    filename="example.log", 
    filemode="a", 
    encoding='utf-8'
    )

# 사용
log = logging.getLogger(__name__)

logging.debug('망할 년들이')    
logging.info('얼마나 대단한 정보를 정리했다고')    
logging.warning('복사를 못하게 막아놓냐')
logging.error('그딴 심성을 가지고 뭔 개발을 하겠다고')
logging.critical('너넨 평생 딱 월급만큼만 벌거다.')

```