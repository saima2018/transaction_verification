# layer2

1. 链上链下信息同步：geth2mysql.py main()持续扫块并同步链上信息到mysql

2. 周期性生成验证信息：merkle.py的 storeMerkleTree方法周期性执行，生成并保存当前周期所有交易组成的merkle tree及相关验证信息到txt文件，以交易id范围命名区分。

3. 验证（http服务）： 用户首先调用merkle.py的getProof方法获取自身账户对应的证据，随后将证据输入链上合约验证真伪。

4. 首次启动时，start_id.txt文件须已经存在，保存值0.

部署流程：

1. 启动私链浏览器，打开mongo数据库 xx.xx.xx.xx:27017  无密码
2. 启动项目中merkle.py 开始按设定周期打包生成 txt文件。同时开放proof获取服务，可通过xx.xx.xx.xx:2306 post请求获取。
3. 打开remix，到下方的合约地址输入相关数据进行验证。


私链交易验证合约：0xxxxxxxxxxxxxxxxxxxxxxxxxx


##############################3
obsolete

Ropsten: 0xxxxxxxxxxx
BSC Testnet: 0xxxxxxxxxxxxxxxxxx
account 2 部署：0xxxxxxxxxxxxxxxxxxxx

部署流程：
1. docker start mysql1容器，navicat打开mysql1连接，block表的最大id不为空
	1.5 链上链下信息同步：geth2mysql.py main()将先找到block表的最大id，从id开始持续扫块并同步链上信息到mysql
		在connect_web3方法里配置私链url

2. 运行merkle.py，设置好发送root hash的公链，数据库等，运行即可自动生成treexxx.txt文件。
	在postman中的body, form-data里传入地址参数，获取该地址的验证信息。


3. 首次启动时，start_id.txt文件须已经存在，保存值0.

1. 链上链下信息同步：geth2mysql.py main()持续扫块并同步链上信息到mysql

2. 周期性生成验证信息：merkle.py的 storeMerkleTree方法周期性执行，生成并保存当前周期所有交易组成的merkle tree及相关验证信息到txt文件，以交易id范围命名区分。

3. 验证（http服务）： 用户首先调用merkle.py的getProof方法获取自身账户对应的证据，随后将证据输入链上合约验证真伪
