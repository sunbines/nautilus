set(msg_srcs
  DispatchQueue.cc
  Message.cc
  Messenger.cc
  QueueStrategy.cc
  msg_types.cc)

list(APPEND msg_srcs
  async/AsyncConnection.cc
  async/AsyncMessenger.cc
  async/Protocol.cc
  async/ProtocolV1.cc
  async/ProtocolV2.cc
  async/Event.cc
  async/EventSelect.cc
  async/PosixStack.cc
  async/Stack.cc
  async/crypto_onwire.cc
  async/frames_v2.cc
  async/net_handler.cc)

if(LINUX)
  list(APPEND msg_srcs
    async/EventEpoll.cc)
elseif(FREEBSD OR APPLE)
  list(APPEND msg_srcs
    async/EventKqueue.cc)
endif(LINUX)

if(HAVE_RDMA)
  list(APPEND msg_srcs
    async/rdma/Infiniband.cc
    async/rdma/RDMAConnectedSocketImpl.cc
    async/rdma/RDMAIWARPConnectedSocketImpl.cc
    async/rdma/RDMAServerSocketImpl.cc
    async/rdma/RDMAIWARPServerSocketImpl.cc
    async/rdma/RDMAStack.cc)
endif()

add_library(common-msg-objs OBJECT ${msg_srcs})

