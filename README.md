# audio

|— src/                                      	        # 主应用目录
|	|— main.py		        	                        # FastAPI应用入口
|	|— core/				                            # 核心配置和工具
|	|		|—  __init__.py	   
|	|		|— config.py                                # 应用配置
|	|		|— logger.py                                # 日志配置
|	|— api/
|	|	|— __init__.py
|	|	|— v1/
|	|	|	|— __init__.py
|	|	|	|— endpoints/	  	                        # 各个键点 API对应的URL
|	|	|	|	|—asr.py                                # asr API	
|	|	|	|	|—llm.py	                            # llm API
|	|	|	|	|—response.py	                        # response API
|	|	|	|— routers.py	                            # 路由聚合
|	|— models/
|	|	|— SenseVoiceSmall                              # asr模型
|	|— services/                                        # service 具体实现
|	|	|— __init__.py
|	|	|— asr_service.py                               # asr 具体实现                         
|	|	|— llm_service.py                               # llm 具体实现
|	|	|— tts_service.py                               # tts 具体实现
|	|— utils/                                           # 各种工具
|	|	|— __init__.py      
|	|	|— util.py                                      # 工具
|	|	|— opus_encoder_utils.py                        # opus编码器
|— static/                                              # 静态文件
|	|— demo.py		        	                        # 
|	|— core/				                            # 