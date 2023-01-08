# layer2

1. 链上链下信息同步：geth2mysql.py main()持续扫块并同步链上信息到mysql

2. 周期性生成验证信息：merkle.py的 storeMerkleTree方法周期性执行，生成并保存当前周期所有交易组成的merkle tree及相关验证信息到txt文件，以交易id范围命名区分。

3. 验证（http服务）： 用户首先调用merkle.py的getProof方法获取自身账户对应的证据，随后将证据输入链上合约验证真伪。

4. 首次启动时，start_id.txt文件须已经存在，保存值0.
