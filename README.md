# Tic-Tac-Toe AI

Dự án xây dựng trò chơi **Tic-Tac-Toe mở rộng trên bàn cờ 4×4**, sử dụng
Python và các thuật toán trí tuệ nhân tạo để lựa chọn nước đi. Dự án có
giao diện đồ họa bằng Pygame và hỗ trợ chơi Người với Người hoặc Người
với AI.

## 1. Tính năng

-   Bàn cờ kích thước 4×4; điều kiện thắng được cấu hình là 4 quân liên
    tiếp.
-   Hai chế độ:
    -   **PVP:** hai người chơi lần lượt đánh.
    -   **PLAYER VS AI:** người chơi đấu với AI.
-   Sáu AI có thể lựa chọn:
    -   Random
    -   Heuristic
    -   Minimax
    -   Alpha-Beta
    -   MCTS
    -   DQN
-   Trong chế độ Người vs AI, người chơi có thể chọn quân X hoặc O.
-   Có nút khởi động lại trận đấu và phím tắt `R`.
-   Hiển thị lượt chơi, kết quả và thống kê số trận thắng của X, O và số
    trận hòa.

## 2. Công nghệ sử dụng

-   Python
-   Pygame: xây dựng giao diện trò chơi.
-   NumPy và PyTorch: xử lý dữ liệu trạng thái và mô hình DQN.
-   Jupyter Notebook: môi trường phát triển, thử nghiệm và phân tích.

## 3. Cấu trúc thư mục

Cấu trúc tổng quát của dự án:

``` text
TicTacToe_AI/
├── agents/
│   ├── random_agent.py
│   ├── heuristic_agent.py
│   ├── minimax_agent.py
│   ├── alphabeta_agent.py
│   ├── mcts_agent.py
│   ├── dqn_agent.py
│   ├── dqn_network.py
│   └── replay_buffer.py
├── game/
│   ├── board.py
│   ├── game_engine.py
│   ├── rules.py
│   └── state.py
├── models/
│   └── dqn_tictactoe.pth
├── notebooks/
├── results/
├── tests/
├── training/
├── ui/
│   ├── agent_manager.py
│   └── game_ui.py
├── experiments/
├── requirements.txt
└── README.md
```

Một số thư mục có thể chứa thêm tệp notebook, kết quả thí nghiệm hoặc mã
nguồn phụ trợ.

## 4. Yêu cầu trước khi cài đặt

-   Đã cài Python và `pip`.
-   Có đầy đủ mã nguồn của dự án.
-   Có tệp trọng số mô hình DQN tại:

``` text
models/dqn_tictactoe.pth
```

**Lưu ý:** `ui/agent_manager.py` tải mô hình DQN ngay khi khởi tạo bộ
quản lý AI. Nếu thiếu tệp trọng số trên, chương trình sẽ báo
`FileNotFoundError` và không khởi chạy bình thường.

## 5. Cài đặt trên Windows

Mở Terminal, PowerShell hoặc Anaconda Prompt.

### Bước 1: Di chuyển đến thư mục dự án

Thay đường dẫn dưới đây nếu bạn đặt dự án ở vị trí khác:

``` powershell
cd D:\TTNTNC\TicTacToe_AI
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)

Nếu sử dụng `venv`:

``` powershell
python -m venv .venv
```

Kích hoạt môi trường:

``` powershell
.venv\Scripts\activate
```

Nếu bạn đã có môi trường Conda riêng cho dự án, hãy kích hoạt môi trường
đó thay vì tạo thêm `venv`:

``` powershell
conda activate tictactoe-ai
```

### Bước 3: Cài đặt các thư viện

Cài các thư viện được liệt kê trong `requirements.txt`:

``` powershell
python -m pip install -r requirements.txt
```

Tệp `requirements.txt` hiện liệt kê NumPy, Pandas, Matplotlib, Pytest,
IPykernel và Jupyter. Mã nguồn giao diện và bộ quản lý AI còn sử dụng
**Pygame** và **PyTorch**, vì vậy cần cài thêm:

``` powershell
python -m pip install pygame torch
```

Nếu PyTorch không cài được hoặc bạn muốn sử dụng GPU NVIDIA, hãy chọn
lệnh cài đặt phù hợp với hệ điều hành, phiên bản Python và phiên bản
CUDA trên máy từ trang hướng dẫn chính thức của PyTorch:
https://pytorch.org/get-started/locally/

### Bước 4: Kiểm tra các thư viện

``` powershell
python -c "import pygame, torch, numpy; print('Pygame:', pygame.version.ver); print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
```

Dòng `CUDA available: True` cho biết PyTorch nhận diện được CUDA. Nếu là
`False`, chương trình vẫn có thể chạy bằng CPU, nhưng tốc độ xử lý DQN
có thể khác.

## 6. Khởi chạy trò chơi

Đảm bảo Terminal đang ở thư mục gốc `TicTacToe_AI`, sau đó chạy:

``` powershell
python -m ui.game_ui
```

Không chạy lệnh này khi đang đứng bên trong thư mục `ui`; hãy chạy từ
thư mục gốc để Python tìm được các package `game`, `agents` và `ui`.

## 7. Cách chơi

### Chọn chế độ

-   **PVP:** chơi hai người trên cùng máy.
-   **PLAYER VS AI:** chơi với AI được chọn.

### Chọn AI

Trong chế độ PLAYER VS AI, sử dụng nút mũi tên trái/phải để chuyển giữa
sáu AI.

### Chọn quân cờ

-   Chọn **X** nếu muốn đi trước.
-   Chọn **O** nếu muốn AI đi trước (X là người đi đầu theo luật hiện
    tại).

### Thực hiện nước đi

Nhấp chuột vào một ô trống trên bàn cờ. Trong chế độ Người vs AI, chỉ có
thể đánh khi đến lượt người chơi.

### Khởi động lại

-   Nhấn nút **RESTART (R)** trên giao diện.
-   Hoặc nhấn phím `R`.

## 8. Chạy Notebook và kiểm thử

### Mở Jupyter Notebook

Từ thư mục gốc dự án:

``` powershell
jupyter notebook
```

Các notebook phục vụ xây dựng Game Engine, phát triển agent, huấn luyện
DQN và thực hiện thí nghiệm nằm trong thư mục `notebooks/`.

### Chạy kiểm thử

Nếu dự án có các bài kiểm thử trong thư mục `tests/`, chạy:

``` powershell
python -m pytest tests
```

## 9. Một số lỗi thường gặp

### Lỗi `ModuleNotFoundError: No module named 'pygame'`

Cài Pygame trong đúng môi trường Python đang dùng:

``` powershell
python -m pip install pygame
```

### Lỗi `ModuleNotFoundError: No module named 'torch'`

Cài PyTorch:

``` powershell
python -m pip install torch
```

### Lỗi `FileNotFoundError: Không tìm thấy mô hình DQN`

Kiểm tra tệp sau có tồn tại hay không:

``` text
TicTacToe_AI/models/dqn_tictactoe.pth
```

Không đổi tên hoặc di chuyển tệp nếu chưa cập nhật đường dẫn mô hình
trong mã nguồn.

### Lỗi `ModuleNotFoundError` với `game` hoặc `agents`

Đảm bảo bạn chạy lệnh từ thư mục gốc dự án:

``` powershell
cd D:\TTNTNC\TicTacToe_AI
python -m ui.game_ui
```

Kiểm tra các thư mục `game`, `agents`, `ui` có tệp `__init__.py`.

### Chương trình chạy nhưng không mở giao diện

Kiểm tra Pygame đã được cài trong đúng môi trường và thử lệnh kiểm tra ở
phần cài đặt. Khi khởi chạy, xem nội dung lỗi được in trong Terminal.

## 10. Ghi chú

-   Kích thước bàn cờ và độ dài chuỗi thắng hiện được truyền vào Game
    Engine là `4` và `4`.
-   Bộ quản lý AI khởi tạo Minimax và Alpha-Beta ở depth 4, MCTS với
    1.000 simulations.
-   DQN được nạp từ checkpoint `models/dqn_tictactoe.pth` và đặt ở chế
    độ đánh giá khi chơi.
-   Notebook dùng cho quá trình phát triển và phân tích; để mở giao diện
    game, không cần khởi chạy Jupyter Notebook.
