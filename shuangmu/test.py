import cv2


def main():
    cap1 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(2)

    cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap1.set(cv2.CAP_PROP_FPS, 30)
    cap2.set(cv2.CAP_PROP_FPS, 30)

    cap1.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    cap2.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    out = cv2.VideoWriter('zhongcai_0927-50.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 15.0, (1920 * 2, 1080))

    if not cap1.isOpened() or not cap2.isOpened():
        print("Error: Unable to open one or both cameras")
        exit()

    while True:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        frame = cv2.hconcat([frame1, frame2])

        out.write(frame)

        if not ret1 or not ret2:
            print("Can't receive frame from one or both cameras. Exiting ...")
            break
        cv2.imshow('Camera ', frame)

        # 按'q'键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap1.release()
    cap2.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()