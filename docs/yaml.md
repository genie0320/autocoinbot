# 애증의 yaml

처음엔 yaml까지 다루고 싶은 마음은 전혀 없었다. 뭐 얼마나 개발개발한 개발을 하겠다고 내가 yaml을... docker나 poetry를 포기하면서 함께 포기되었던 yaml.

하지만... 얼핏 살펴보면서 너.무.나 자유로운 그 형식때문에 온종일 yaml이라면...이라는 잡생각이 떠나지 않았고, 오늘 하루를 또 꼬박 투자해서 yaml의 특성을 대략 알아냈다.

급하니까 일단 다음은... yaml 파일을 저장하는 코드이다. 경로와 데이터(dict형태)를 주면 알아서 업데이트하거나 추가해준다.

```python
def save_yaml(file_path, **datas):
    '''
    yaml 파일을 생성한다.
    
    - file_path : yaml 파일의 경로
    - datas : yaml 파일에 저장할 데이터(dictionary)
    '''
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            placeholder = dict()
            yaml.safe_dump(placeholder, f, allow_unicode=True, default_flow_style=False)

    with open(file_path, 'r') as f:
        _data = yaml.safe_load(f)

    for k, v in datas.items():
        _data[k] = v
    with open(file_path, 'w') as f:
        yaml.safe_dump(_data, f, allow_unicode=True, default_flow_style=False)

# 사용시
save_yaml('data/report.yml', **{f'coins_of_{interval}': sorted_coin})

```

## 깨달은점
한참을 헤매고 실험한 끝에 알아낸 사실인데. yaml로 저장된 파일을 update하는 경우, 읽어온 기존 데이터의 형태에 영향을 받는다. 기존에 저장된 데이터(읽어온 데이터)의 형식에 따라 업데이트하는 방식이 달라진다. 

str > str + data(str)
list > list.append(data), expand(data)
dict > dict.update(data)

물론, 전천후 함수를 만들려고 시도도 했으나... dict 와 <class 'dict'>가 또 다른 것을 보고 일단은 포기했다. 